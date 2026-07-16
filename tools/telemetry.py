#!/usr/bin/env python3
"""Append-only daily TOML telemetry with value redaction and span correlation."""
from __future__ import annotations
import argparse, contextlib, datetime as dt, json, math, os, platform, re, stat, time, uuid
from pathlib import Path
from typing import Any
try:
    from security_utils import ensure_no_symlink_components
except ImportError:
    from tools.security_utils import ensure_no_symlink_components

SUITE_ROOT=Path(__file__).resolve().parents[1]
DEFAULT_DIR=Path(os.environ.get('MD_LOG_DIR',SUITE_ROOT/'.prompt_suite'/'logs'))
SENSITIVE_KEY_RE=re.compile(r'secret|token|password|passwd|credential|private[_-]?key|api[_-]?key|authorization|cookie',re.I)

VALID_STATUSES={'started','progress','pass','fail','blocked','cancelled','info'}
MAX_TEXT_CHARS=100_000
MAX_COLLECTION_ITEMS=1_000
MAX_NESTING_DEPTH=12
MAX_EVENT_BYTES=1_048_576
IDENTIFIER_RE=re.compile(r'^[A-Za-z0-9_.:-]{1,256}$')
REQUIRED_EVENT_FIELDS={'event_id','span_id','parent_span_id','timestamp_utc','timestamp_local','date_local','category','action','status','duration_ms','tool','run_id','platform','process_id'}

def validate_event(event:dict[str,Any])->None:
    missing=sorted(REQUIRED_EVENT_FIELDS-set(event))
    if missing: raise ValueError(f'Missing telemetry fields: {missing}')
    if event['status'] not in VALID_STATUSES: raise ValueError(f'Invalid telemetry status: {event["status"]}')
    for field in ('category','action','tool','run_id','span_id'):
        value=event.get(field)
        if not isinstance(value,str) or not IDENTIFIER_RE.fullmatch(value):
            raise ValueError(f'Telemetry {field} must be 1-256 safe identifier characters')
    parent=event.get('parent_span_id','')
    if parent and (not isinstance(parent,str) or not IDENTIFIER_RE.fullmatch(parent)):
        raise ValueError('Telemetry parent_span_id is invalid')
    for field in ('prompt_id','scenario_id'):
        value=event.get(field,'')
        if value and (not isinstance(value,str) or not IDENTIFIER_RE.fullmatch(value)):
            raise ValueError(f'Telemetry {field} is invalid')
    if not isinstance(event['duration_ms'],int) or event['duration_ms']<0: raise ValueError('Telemetry duration_ms must be a non-negative integer')
    encoded=json.dumps(event,ensure_ascii=False,default=str,separators=(',',':')).encode('utf-8')
    if len(encoded)>MAX_EVENT_BYTES: raise ValueError(f'Telemetry event exceeds {MAX_EVENT_BYTES} bytes')

VALUE_PATTERNS=[
 re.compile(r'(?i)(bearer\s+)[A-Za-z0-9._~+\-/=]{8,}'),
 re.compile(r'(?i)(api[_-]?key\s*[:=]\s*)[^\s,;]+'),
 re.compile(r'(?i)(password\s*[:=]\s*)[^\s,;]+'),
 re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----',re.S),
 re.compile(r'(?i)(https?://[^\s/:]+:)[^@\s]+@'),
 re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
 re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}\b'),
 re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{10,}\b'),
 re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b'),
 re.compile(r'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b'),
]

def _redact_text(value:str)->str:
    out=value
    for pattern in VALUE_PATTERNS:
        if 'PRIVATE KEY' in pattern.pattern: out=pattern.sub('[REDACTED PRIVATE KEY]',out)
        else: out=pattern.sub(lambda m:(m.group(1) if m.lastindex else '')+'[REDACTED]',out)
    return out

def _redact(value:Any,key:str='',*,_depth:int=0,_seen:set[int]|None=None)->Any:
    if SENSITIVE_KEY_RE.search(key): return '[REDACTED]'
    if _depth>MAX_NESTING_DEPTH: raise ValueError(f'Telemetry nesting exceeds {MAX_NESTING_DEPTH}')
    if _seen is None: _seen=set()
    if isinstance(value,str):
        if len(value)>MAX_TEXT_CHARS: raise ValueError(f'Telemetry text exceeds {MAX_TEXT_CHARS} characters')
        return _redact_text(value)
    if isinstance(value,dict):
        if len(value)>MAX_COLLECTION_ITEMS: raise ValueError('Telemetry object has too many fields')
        marker=id(value)
        if marker in _seen: raise ValueError('Telemetry values must not contain cycles')
        _seen.add(marker)
        try:
            out={}
            for raw_key,raw_value in value.items():
                string_key=str(raw_key)
                if len(string_key)>256 or any(ord(ch)<32 for ch in string_key):
                    raise ValueError('Telemetry keys must be at most 256 characters without control characters')
                if string_key in out: raise ValueError(f'Telemetry key collision after string conversion: {string_key}')
                out[string_key]=_redact(raw_value,string_key,_depth=_depth+1,_seen=_seen)
            return out
        finally: _seen.remove(marker)
    if isinstance(value,(list,tuple)):
        if len(value)>MAX_COLLECTION_ITEMS: raise ValueError('Telemetry collection has too many items')
        marker=id(value)
        if marker in _seen: raise ValueError('Telemetry values must not contain cycles')
        _seen.add(marker)
        try: return [_redact(item,key,_depth=_depth+1,_seen=_seen) for item in value]
        finally: _seen.remove(marker)
    return value

@contextlib.contextmanager
def _file_lock(lock_path:Path):
    lock_path=ensure_no_symlink_components(lock_path)
    lock_path.parent.mkdir(parents=True,exist_ok=True)
    ensure_no_symlink_components(lock_path.parent)
    flags=os.O_RDWR|os.O_CREAT
    if hasattr(os,'O_NOFOLLOW'): flags|=os.O_NOFOLLOW
    fd=os.open(lock_path,flags,0o600)
    try:
        opened=os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink!=1:
            raise ValueError(f'Lock path must be a single-link regular file: {lock_path}')
        try: os.chmod(lock_path,0o600)
        except OSError: pass
        with os.fdopen(fd,'r+b',closefd=False) as lock:
            if os.name=='nt':
                import msvcrt
                lock.seek(0); lock.write(b'0'); lock.flush(); lock.seek(0); msvcrt.locking(lock.fileno(),msvcrt.LK_LOCK,1)
                try: yield
                finally: lock.seek(0); msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
            else:
                import fcntl
                fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
                try: yield
                finally: fcntl.flock(lock.fileno(),fcntl.LOCK_UN)
    finally:
        os.close(fd)

def _q(value:str)->str:
    # JSON basic strings are valid TOML basic strings and correctly escape all
    # control characters, including NUL, backspace, and form feed.
    return json.dumps(value,ensure_ascii=False)

def _scalar(v:Any)->str:
    if v is None: return _q('')
    if isinstance(v,bool): return 'true' if v else 'false'
    if isinstance(v,int) and not isinstance(v,bool): return str(v)
    if isinstance(v,float):
        return str(v) if math.isfinite(v) else _q(str(v))
    if isinstance(v,(dict,list,tuple)): return _q(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')))
    return _q(str(v))

def _key(value:str)->str:
    value=str(value)
    return value if re.fullmatch(r'[A-Za-z0-9_-]+',value) else _q(value)

def _flat(prefix:str,obj:dict[str,Any])->list[str]:
    out=[]
    for key,val in sorted(obj.items(),key=lambda item:str(item[0])):
        segment=_key(str(key)); full=f'{prefix}.{segment}' if prefix else segment
        if isinstance(val,dict): out.extend(_flat(full,val))
        elif isinstance(val,list) and all(not isinstance(x,(dict,list,tuple)) for x in val): out.append(f'{full} = ['+', '.join(_scalar(x) for x in val)+']')
        else: out.append(f'{full} = {_scalar(val)}')
    return out

def append_event(category:str,action:str,status:str='info',*,duration_ms:int=0,tool:str='md',run_id:str='',span_id:str='',parent_span_id:str='',prompt_id:str|None=None,scenario_id:str|None=None,metrics:dict[str,Any]|None=None,context:dict[str,Any]|None=None,references:list[str]|None=None,error:str|None=None,log_dir:Path|None=None)->dict[str,Any]:
    now_local=dt.datetime.now().astimezone(); now_utc=now_local.astimezone(dt.timezone.utc)
    if isinstance(duration_ms,bool) or not isinstance(duration_ms,int) or duration_ms<0:
        raise ValueError('Telemetry duration_ms must be a non-negative integer')
    run=run_id or os.environ.get('MD_RUN_ID') or str(uuid.uuid4())
    event={'event_id':str(uuid.uuid4()),'span_id':span_id or str(uuid.uuid4()),'parent_span_id':parent_span_id,'timestamp_utc':now_utc.isoformat(),'timestamp_local':now_local.isoformat(),'date_local':now_local.date().isoformat(),'category':category,'action':action,'status':status,'duration_ms':duration_ms,'tool':tool,'run_id':run,'prompt_id':prompt_id or '','scenario_id':scenario_id or '','platform':platform.system().lower(),'process_id':os.getpid(),'metrics':_redact(metrics or {}),'context':_redact(context or {}),'references':_redact(references or []),'error':_redact_text(error or '')}
    validate_event(event)
    directory=ensure_no_symlink_components(Path(log_dir or DEFAULT_DIR)); directory.mkdir(parents=True,exist_ok=True); ensure_no_symlink_components(directory); path=directory/f"{event['date_local']}.toml"
    lines=['[[events]]']
    for key in ['event_id','span_id','parent_span_id','timestamp_utc','timestamp_local','date_local','category','action','status','duration_ms','tool','run_id','prompt_id','scenario_id','platform','process_id','error']:
        lines.append(f'{key} = {_scalar(event[key])}')
    lines.append('references = ['+', '.join(_scalar(x) for x in event['references'])+']'); lines.extend(_flat('metrics',event['metrics'])); lines.extend(_flat('context',event['context'])); lines.append('')
    with _file_lock(path.with_suffix(path.suffix+'.lock')):
        first=not path.exists()
        flags=os.O_WRONLY|os.O_CREAT|os.O_APPEND
        if hasattr(os,'O_NOFOLLOW'): flags|=os.O_NOFOLLOW
        fd=os.open(path,flags,0o600)
        try:
            opened=os.fstat(fd)
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink!=1:
                raise ValueError(f'Log path must be a single-link regular file: {path}')
            try: os.chmod(path,0o600)
            except OSError: pass
            with os.fdopen(fd,'a',encoding='utf-8',newline='\n',closefd=False) as fh:
                if first: fh.write(f'# MD daily append-only telemetry\n# date_local = {event["date_local"]}\n# schema = schemas/daily_log_event.schema.json\n\n')
                fh.write('\n'.join(lines)+'\n'); fh.flush(); os.fsync(fh.fileno())
        finally:
            os.close(fd)
    event['log_file']=str(path); return event

class EventTimer:
    def __init__(self,category:str,action:str,**kwargs):
        self.category=category; self.action=action; self.kwargs=kwargs; self.start=0.0; self.run_id=kwargs.pop('run_id','') or os.environ.get('MD_RUN_ID') or str(uuid.uuid4()); self.span_id=str(uuid.uuid4())
    def __enter__(self):
        self.start=time.perf_counter(); append_event(self.category,self.action,'started',run_id=self.run_id,span_id=self.span_id,**self.kwargs); return self
    def __exit__(self,exc_type,exc,tb):
        append_event(self.category,self.action,'fail' if exc else 'pass',duration_ms=int((time.perf_counter()-self.start)*1000),error=str(exc) if exc else None,run_id=self.run_id,span_id=self.span_id,**self.kwargs); return False

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    x=sub.add_parser('append'); x.add_argument('--category',required=True); x.add_argument('--action',required=True); x.add_argument('--status',default='info'); x.add_argument('--duration-ms',type=int,default=0); x.add_argument('--tool',default='cli'); x.add_argument('--run-id',default=''); x.add_argument('--span-id',default=''); x.add_argument('--prompt-id'); x.add_argument('--scenario-id'); x.add_argument('--metrics-json',default='{}'); x.add_argument('--context-json',default='{}'); x.add_argument('--reference',action='append',default=[]); x.add_argument('--error')
    sub.add_parser('path'); a=ap.parse_args()
    if a.cmd=='path': print(DEFAULT_DIR/f'{dt.datetime.now().astimezone().date().isoformat()}.toml'); return
    print(json.dumps(append_event(a.category,a.action,a.status,duration_ms=a.duration_ms,tool=a.tool,run_id=a.run_id,span_id=a.span_id,prompt_id=a.prompt_id,scenario_id=a.scenario_id,metrics=json.loads(a.metrics_json),context=json.loads(a.context_json),references=a.reference,error=a.error),indent=2))
if __name__=='__main__': main()
