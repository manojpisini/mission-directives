from __future__ import annotations
import sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from tui import TUI
from telemetry import append_event
_tui=None; _start=0.0
def pytest_sessionstart(session):
 global _start
 _start=time.perf_counter(); append_event('test','pytest_session','started',tool='pytest')
def pytest_collection_finish(session):
 global _tui
 _tui=TUI('MD deterministic tests',max(1,len(session.items))); _tui.start()
def pytest_runtest_logreport(report):
 if report.when=='call' and _tui: _tui.step(report.nodeid)
def pytest_sessionfinish(session,exitstatus):
 if _tui: _tui.finish('PASS' if exitstatus==0 else 'FAIL')
 append_event('test','pytest_session','pass' if exitstatus==0 else 'fail',duration_ms=int((time.perf_counter()-_start)*1000),tool='pytest',metrics={'exit_status':exitstatus,'test_count':len(getattr(session,'items',[]))})
