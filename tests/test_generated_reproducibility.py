from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
def load():
 spec=importlib.util.spec_from_file_location('generated_repro',ROOT/'tools/check_generated_reproducibility.py'); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def test_generated_views_are_byte_reproducible():
 result=load().check(ROOT)
 assert result['status']=='pass',result
