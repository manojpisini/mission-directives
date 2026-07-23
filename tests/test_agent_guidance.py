from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sync_agent_guidance", ROOT / "tools" / "sync_agent_guidance.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_creates_only_agents_and_claude_without_erasing_content(tmp_path: Path):
    existing = tmp_path / "CLAUDE.md"
    existing.write_text("# Existing Claude rules\n\nKeep this exact text.\n", encoding="utf-8")
    receipt = module.sync_guidance(project_root=tmp_path, suite_root=ROOT)
    assert receipt["status"] == "changed"
    assert module.DEFAULT_AGENT_FILES == ["AGENTS.md", "CLAUDE.md"]
    for name in module.DEFAULT_AGENT_FILES:
        path = tmp_path / name
        assert path.exists(), name
        text = path.read_text(encoding="utf-8")
        assert module.BEGIN_MARKER in text and module.END_MARKER in text
        assert "prompts/" in text and "catalog.json" in text and "SCENARIO_CATALOG.json" in text
    for excluded in ["CODEX.md", "PI.md", "HERMES.md", "OPENCODE.md", "GEMINI.md"]:
        assert not (tmp_path / excluded).exists(), excluded
    assert existing.read_text(encoding="utf-8").startswith("# Existing Claude rules\n\nKeep this exact text.\n")


def test_rerun_is_idempotent_and_does_not_duplicate_managed_block(tmp_path: Path):
    first = module.sync_guidance(project_root=tmp_path, suite_root=ROOT)
    before = {name: (tmp_path / name).read_text(encoding="utf-8") for name in module.DEFAULT_AGENT_FILES}
    second = module.sync_guidance(project_root=tmp_path, suite_root=ROOT)
    after = {name: (tmp_path / name).read_text(encoding="utf-8") for name in module.DEFAULT_AGENT_FILES}
    assert first["changed_files"]
    assert second["status"] == "unchanged"
    assert not second["changed_files"]
    assert before == after
    assert all(text.count(module.BEGIN_MARKER) == 1 for text in after.values())


def test_updates_only_managed_block_when_suite_location_changes(tmp_path: Path):
    file_path = tmp_path / "AGENTS.md"
    file_path.write_text("Human-owned prefix.\n", encoding="utf-8")
    module.sync_guidance(project_root=tmp_path, suite_root=ROOT, agent_files=["AGENTS.md"])
    first = file_path.read_text(encoding="utf-8")
    alt_suite = tmp_path / "vendor" / "md"
    alt_suite.mkdir(parents=True)
    for filename in ["VERSION", "catalog.json", "SCENARIO_CATALOG.json", "skill_registry.json"]:
        source = ROOT / filename
        (alt_suite / filename).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (alt_suite / "config").mkdir()
    for filename in ["department_packs.json"]:
        (alt_suite / "config" / filename).write_text((ROOT / "config" / filename).read_text(encoding="utf-8"), encoding="utf-8")
    (alt_suite / "policies").mkdir()
    for filename in ["agent_guidance_policy.json"]:
        (alt_suite / "policies" / filename).write_text((ROOT / "policies" / filename).read_text(encoding="utf-8"), encoding="utf-8")
    (alt_suite / "prompts").mkdir()
    (alt_suite / "tools").mkdir()
    (alt_suite / "docs").mkdir()
    module.sync_guidance(project_root=tmp_path, suite_root=alt_suite, agent_files=["AGENTS.md"])
    second = file_path.read_text(encoding="utf-8")
    assert first != second
    assert second.startswith("Human-owned prefix.\n")
    assert second.count(module.BEGIN_MARKER) == 1
    assert "vendor/md" in second.replace("\\", "/")


def test_dry_run_writes_nothing_and_reports_changes(tmp_path: Path):
    receipt = module.sync_guidance(project_root=tmp_path, suite_root=ROOT, dry_run=True)
    assert receipt["status"] == "dry_run_changes"
    assert receipt["changed_files"]
    assert not any((tmp_path / name).exists() for name in module.DEFAULT_AGENT_FILES)


def test_remove_deletes_only_managed_block_and_preserves_file(tmp_path: Path):
    target = tmp_path / "CLAUDE.md"
    target.write_text("# Human rules\n", encoding="utf-8")
    module.sync_guidance(project_root=tmp_path, suite_root=ROOT, agent_files=["CLAUDE.md"])
    receipt = module.sync_guidance(project_root=tmp_path, suite_root=ROOT, agent_files=["CLAUDE.md"], remove=True)
    assert receipt["status"] == "changed"
    text = target.read_text(encoding="utf-8")
    assert text == "# Human rules\n"
    assert module.BEGIN_MARKER not in text


def test_supported_subset_and_receipt_output(tmp_path: Path):
    receipt_path = tmp_path / ".prompt_suite" / "agent-guidance-receipt.json"
    receipt = module.sync_guidance(
        project_root=tmp_path,
        suite_root=ROOT,
        agent_files=["AGENTS.md"],
        receipt_path=receipt_path,
    )
    assert receipt_path.exists()
    saved = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert saved["managed_files"] == ["AGENTS.md"]
    assert receipt["receipt_path"].endswith("agent-guidance-receipt.json")


def test_rejects_any_agent_filename_other_than_agents_or_claude(tmp_path: Path):
    for bad in ["CODEX.md", "PI.md", "HERMES.md", "OPENCODE.md", "CUSTOM_AGENT.md", "../AGENTS.md", "/tmp/AGENTS.md", "AGENTS.txt"]:
        try:
            module.sync_guidance(project_root=tmp_path, suite_root=ROOT, agent_files=[bad])
            assert False, bad
        except ValueError:
            pass


def test_rendered_guidance_contains_lookup_and_auto_orchestration_rules(tmp_path: Path):
    text = module.render_guidance(project_root=tmp_path, suite_root=ROOT, agent_file="AGENTS.md")
    for token in [
        "tools/md.py route",
        "tools/md.py compare",
        "tools/md.py lookup",
        "tools/md.py explain",
        "MD-191",
        "MD-198",
        "visual-assets",
        "strudel",
        "smallest coherent graph",
        "Do not load every prompt",
        "Only AGENTS.md and CLAUDE.md",
        "exact execution twin",
        "pair-status",
        "tools/keyword_context.py",
        "Do not read prompt bodies during intent selection",
    ]:
        assert token in text


def test_malformed_marker_file_is_not_modified(tmp_path: Path):
    target = tmp_path / "AGENTS.md"
    original = "Human rules\n" + module.BEGIN_MARKER + "\nunterminated\n"
    target.write_text(original, encoding="utf-8")
    try:
        module.sync_guidance(project_root=tmp_path, suite_root=ROOT, agent_files=["AGENTS.md"])
        assert False
    except ValueError as exc:
        assert "unmatched" in str(exc)
    assert target.read_text(encoding="utf-8") == original


def test_powershell_and_cmd_wrappers_delegate_to_python_sync_tool():
    ps = (ROOT / "tools" / "sync-agent-guidance.ps1").read_text(encoding="utf-8")
    cmd = (ROOT / "tools" / "sync-agent-guidance.cmd").read_text(encoding="utf-8")
    assert "sync_agent_guidance.py" in ps
    assert "$ProjectRoot" in ps and "$SuiteRoot" in ps
    assert "AllKnown" not in ps
    assert "sync-agent-guidance.ps1" in cmd
