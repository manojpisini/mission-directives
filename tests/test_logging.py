from pathlib import Path
import sys,datetime as dt
try: import tomllib
except ImportError: import tomli as tomllib
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'tools'))
from telemetry import append_event
def test_daily_toml_append_and_parse(tmp_path):
 a=append_event('test','one','pass',tool='pytest',log_dir=tmp_path,context={'quote':'a"b','unicode':'✓'})
 b=append_event('test','two','fail',tool='pytest',log_dir=tmp_path,error='expected',metrics={'n':2})
 assert a['log_file']==b['log_file']
 data=tomllib.loads(Path(a['log_file']).read_text(encoding='utf-8')); assert [x['action'] for x in data['events']]==['one','two']; assert data['events'][1]['metrics']['n']==2
def test_log_filename_is_local_date(tmp_path):
 e=append_event('test','date','pass',log_dir=tmp_path); assert Path(e['log_file']).stem==dt.datetime.now().astimezone().date().isoformat()


def test_sensitive_keys_are_redacted(tmp_path):
 e=append_event('test','redact','pass',log_dir=tmp_path,context={'api_token':'abc','nested':{'password':'xyz'},'safe':'ok'})
 data=tomllib.loads(Path(e['log_file']).read_text()); row=data['events'][0]
 assert row['context']['api_token']=='[REDACTED]'
 assert row['context']['nested']['password']=='[REDACTED]'
 assert row['context']['safe']=='ok'


def test_secret_like_values_are_redacted_and_spans_correlate(tmp_path):
 from telemetry import EventTimer
 with EventTimer('test','secret',tool='pytest',log_dir=tmp_path,context={'message':'Authorization: Bearer abcdefghijklmnop'}):
  pass
 files=list(tmp_path.glob('*.toml')); data=tomllib.loads(files[0].read_text(encoding='utf-8')); rows=data['events']
 assert len(rows)==2; assert rows[0]['run_id']==rows[1]['run_id']; assert rows[0]['span_id']==rows[1]['span_id']; assert '[REDACTED]' in rows[0]['context']['message']

def test_non_finite_and_nested_metric_values_remain_valid_toml(tmp_path):
 e=append_event('test','complex','pass',log_dir=tmp_path,metrics={'nan':float('nan'),'nested_list':[{'a':1}]})
 data=tomllib.loads(Path(e['log_file']).read_text(encoding='utf-8')); assert data['events'][0]['metrics']['nan']=='nan'


def test_invalid_status_is_rejected_before_write(tmp_path):
 import pytest
 with pytest.raises(ValueError): append_event('tool','bad','not-a-status',log_dir=tmp_path)
 assert not list(tmp_path.glob('*.toml'))
