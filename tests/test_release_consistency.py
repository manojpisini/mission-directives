from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
def test_release_metadata_and_distribution_paths_are_consistent():
 spec=importlib.util.spec_from_file_location('release_check',ROOT/'tools/check_release_consistency.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
 result=mod.check(ROOT); assert result['status']=='pass',result
