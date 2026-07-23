from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_every_shell_has_powershell_and_reverse():
    sh = {p.stem for p in (ROOT / "tools").glob("*.sh")}
    ps = {p.stem for p in (ROOT / "tools").glob("*.ps1")}
    assert sh == ps


def test_script_pairs_contain_progress_and_fail_fast():
    for p in (ROOT / "tools").glob("*.sh"):
        text = p.read_text()
        assert "set -euo pipefail" in text
        assert "%" in text
    for p in (ROOT / "tools").glob("*.ps1"):
        text = p.read_text()
        assert "Write-Progress" in text
        assert "ErrorActionPreference" in text


def test_platform_matrix_matches_files():
    d = json.loads((ROOT / "integrations/platform_tool_matrix.json").read_text())
    for row in d["tools"]:
        assert (ROOT / row["bash"]).exists() and (ROOT / row["powershell"]).exists()


def test_ci_matrix_covers_linux_windows_and_macos():
    text = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    for runner in ["ubuntu-latest", "windows-latest", "macos-latest"]:
        assert runner in text


def test_ci_runs_evaluations_and_uploads_review_artifacts():
    text = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    assert "python tools/run_evaluations.py" in text
    assert "python tools/check_script_parity.py" in text
    assert "actions/upload-artifact@v6" in text
    for artifact in [
        "BODY_QUALITY_AUDIT.json",
        "BODY_QUALITY_AUDIT.md",
        "VALIDATION.json",
        ".prompt_suite/results/TEST_RESULTS.json",
        ".prompt_suite/results/EVALUATION_STATUS.json",
    ]:
        assert artifact in text


def test_root_installer_has_bash_and_powershell_launchers():
    assert (
        (ROOT / "tools/install.sh").exists()
        and (ROOT / "tools/install.ps1").exists()
        and (ROOT / "tools/install.py").exists()
    )
    assert "set -euo pipefail" in (ROOT / "tools/install.sh").read_text()
    assert "Write-Progress" in (ROOT / "tools/install.ps1").read_text()
