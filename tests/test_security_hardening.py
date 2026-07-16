from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_skill_id_validation_rejects_path_traversal_and_unsafe_names():
    security = load(ROOT / "tools" / "security_utils.py", "security_utils_skill_id")
    for value in ["../escape", "..\\escape", "/absolute", "C:\\absolute", "", ".", "a/b", "a\\b", "-leading", "trailing-", "two..dots"]:
        with pytest.raises(ValueError):
            security.validate_identifier(value, kind="skill")
    assert security.validate_identifier("visual-assets", kind="skill") == "visual-assets"
    assert security.validate_identifier("skill_v2.1", kind="skill") == "skill_v2.1"


def test_safe_child_refuses_escape_and_symlinked_parent(tmp_path):
    security = load(ROOT / "tools" / "security_utils.py", "security_utils_child")
    base = tmp_path / "base"
    base.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (base / "link").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError):
        security.safe_child(base, "../outside")
    with pytest.raises(ValueError):
        security.ensure_no_symlink_components(base / "link" / "file")
    assert security.safe_child(base, "valid") == base / "valid"


def test_installer_rejects_runtime_symlink_escape(tmp_path):
    installer = load(ROOT / "install.py", "md_install_symlink")
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (project / ".prompt_suite").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        installer.install(project)
    assert not (project / "prompts").exists()
    assert not any(outside.iterdir())


def test_installer_refuses_project_inside_source_tree(tmp_path):
    installer = load(ROOT / "install.py", "md_install_overlap")
    nested = ROOT / "_unsafe_nested_project_for_test"
    try:
        with pytest.raises(ValueError, match="inside the suite source"):
            installer.install(nested, dry_run=True)
    finally:
        if nested.exists():
            import shutil
            shutil.rmtree(nested)


def test_telemetry_preserves_colliding_keys_and_control_characters(tmp_path):
    telemetry = load(ROOT / "tools" / "telemetry.py", "telemetry_collision")
    event = telemetry.append_event(
        "security",
        "collision-test",
        "pass",
        context={"a.b": "one\x00two", "a_b": "three", "nested": {"x-y": 1, "x_y": 2}},
        log_dir=tmp_path,
    )
    import tomllib
    data = tomllib.loads(Path(event["log_file"]).read_text(encoding="utf-8"))
    context = data["events"][0]["context"]
    assert context["a.b"] == "one\u0000two"
    assert context["a_b"] == "three"
    assert context["nested"]["x-y"] == 1
    assert context["nested"]["x_y"] == 2


def test_log_query_rejects_date_path_traversal():
    query = load(ROOT / "tools" / "log_query.py", "log_query_security")
    for value in ["../../secret", "/tmp/secret", "2026-7-1", "not-a-date", "2026-02-30"]:
        with pytest.raises(ValueError):
            query.validate_date(value)
    assert query.validate_date("2026-07-16") == "2026-07-16"


def test_manifest_rejects_symlink_entries(tmp_path):
    manifest = load(ROOT / "tools" / "build_manifest.py", "manifest_symlink")
    root = tmp_path / "suite"
    root.mkdir()
    (root / "VERSION").write_text("1.0.0\n", encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    (root / "linked.txt").symlink_to(outside)
    with pytest.raises(ValueError, match="symbolic link"):
        manifest.current(root)


def test_handoff_hash_requires_sha256_digest():
    md = load(ROOT / "tools" / "md.py", "md_hash_validation")
    for bad in ["x:y", "sha256:short", "md5:" + "0" * 32, "sha256:" + "g" * 64]:
        with pytest.raises(ValueError):
            md.validate_handoff_hash(bad)
    good = "sha256:" + "a" * 64
    assert md.validate_handoff_hash(good) == good


def test_loop_and_metric_numeric_validation_rejects_invalid_values():
    md = load(ROOT / "tools" / "md.py", "md_numeric_validation")
    with pytest.raises(ValueError):
        md.adjudicate_loop(-1, 0.1, 1.0, [])
    with pytest.raises(ValueError):
        md.adjudicate_loop(1, float("nan"), 1.0, [])
    with pytest.raises(ValueError):
        md.validate_metric_inputs(-1, 0, 0, 0, None, None)
    with pytest.raises(ValueError):
        md.validate_metric_inputs(1, 1, 0, 1, float("nan"), None)
    with pytest.raises(ValueError):
        md.validate_metric_inputs(1, 1, 0, 1, None, 6.0)


def test_platform_dispatch_telemetry_does_not_log_raw_arguments():
    text = (ROOT / "tools" / "platform_dispatch.py").read_text(encoding="utf-8")
    assert "'command':' '.join(cmd)" not in text
    assert '"command": cmd' not in text
    assert "arg_count" in text


def test_bootstrap_telemetry_does_not_log_raw_argv():
    text = (ROOT / "tools" / "tool_runtime.py").read_text(encoding="utf-8")
    assert "'argv':' '.join" not in text
    assert "arg_count" in text


def test_runtime_receipts_do_not_mutate_sealed_release_by_default():
    run_tests = (ROOT / "tools" / "run_tests.py").read_text(encoding="utf-8")
    evaluations = (ROOT / "tools" / "run_evaluations.py").read_text(encoding="utf-8")
    inventory = (ROOT / "tools" / "sync_installed_skills.py").read_text(encoding="utf-8")
    assert ".prompt_suite/results/TEST_RESULTS.json" in run_tests
    assert ".prompt_suite/results/EVALUATION_STATUS.json" in evaluations
    assert ".prompt_suite/runtime/installed_skills_inventory.json" in inventory


def test_skills_cli_is_pinned_and_noninteractive():
    text = (ROOT / "tools" / "skill_dual.py").read_text(encoding="utf-8")
    assert "skills@1.5.17" in text
    compact = ''.join(text.split())
    assert "'npx','--yes',SKILLS_CLI_PACKAGE,'add'" in compact
    assert "stdin=subprocess.DEVNULL" in compact
    assert "timeout=SKILLS_CLI_TIMEOUT_SECONDS" in compact


def test_telemetry_rejects_stringified_key_collisions_cycles_and_oversize(tmp_path):
    telemetry = load(ROOT / "tools" / "telemetry.py", "telemetry_limits")
    with pytest.raises(ValueError, match="key collision"):
        telemetry.append_event("security", "collision", context={1: "a", "1": "b"}, log_dir=tmp_path)
    cyclic = {}
    cyclic["self"] = cyclic
    with pytest.raises(ValueError, match="cycles"):
        telemetry.append_event("security", "cycle", context=cyclic, log_dir=tmp_path)
    with pytest.raises(ValueError, match="text exceeds"):
        telemetry.append_event("security", "large", context={"value": "x" * 100_001}, log_dir=tmp_path)


def test_sync_guidance_rejects_symlink_target_and_receipt_escape(tmp_path):
    sync = load(ROOT / "tools" / "sync_agent_guidance.py", "sync_guidance_security")
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("private", encoding="utf-8")
    (project / "AGENTS.md").symlink_to(outside)
    with pytest.raises(ValueError, match="symlink"):
        sync.sync_guidance(project, ROOT, agent_files=["AGENTS.md"])
    (project / "AGENTS.md").unlink()
    with pytest.raises(ValueError, match="inside the project root|Unsafe child path"):
        sync.sync_guidance(project, ROOT, receipt_path="../escaped.json")
    assert not (tmp_path / "escaped.json").exists()


def test_github_repository_validation_rejects_unsafe_transports_and_urls():
    security = load(ROOT / "tools" / "security_utils.py", "security_utils_github")
    assert security.validate_github_repository("https://github.com/owner/repo") == "https://github.com/owner/repo"
    for value in [
        "git@github.com:owner/repo.git",
        "http://github.com/owner/repo",
        "https://user:pass@github.com/owner/repo",
        "https://github.com/owner/repo?x=1",
        "https://evil.example/owner/repo",
        "https://github.com/owner/repo/tree/main",
    ]:
        with pytest.raises(ValueError):
            security.validate_github_repository(value)


def test_local_skill_registration_rolls_back_when_staging_fails(tmp_path, monkeypatch):
    module = load(ROOT / "tools" / "register_local_skill_dual.py", "register_local_rollback")
    source = tmp_path / "source"
    source.mkdir()
    (source / "SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")
    roots = {"agents": tmp_path / "agents", "claude-code": tmp_path / "claude", "opencode": tmp_path / "opencode"}
    monkeypatch.setattr(module, "all_default_destinations", lambda: roots)
    monkeypatch.setattr(module, "append_event", lambda *args, **kwargs: {"log_file": "test"})
    original = module.shutil.copytree
    calls = {"count": 0}

    def fail_second(src, dst, **kwargs):
        calls["count"] += 1
        if calls["count"] == 2:
            raise RuntimeError("forced staging failure")
        return original(src, dst, **kwargs)

    monkeypatch.setattr(module.shutil, "copytree", fail_second)
    monkeypatch.setattr(sys, "argv", ["register_local_skill_dual.py", "--source-directory", str(source), "--skill-id", "demo-skill"])
    with pytest.raises(RuntimeError, match="forced staging failure"):
        module.main()
    assert all(not (root / "demo-skill").exists() for root in roots.values())
    assert not list(tmp_path.rglob("*.stage-*"))


def test_remote_skill_install_rolls_back_all_destinations_on_cli_failure(tmp_path, monkeypatch):
    module = load(ROOT / "tools" / "skill_dual.py", "skill_dual_rollback")
    roots = {"agents": tmp_path / "agents", "claude-code": tmp_path / "claude", "opencode": tmp_path / "opencode"}
    for root in roots.values():
        existing = root / "demo-skill"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("old", encoding="utf-8")
    monkeypatch.setattr(module, "all_default_destinations", lambda: roots)
    monkeypatch.setattr(module, "append_event", lambda *args, **kwargs: {"log_file": "test"})

    class Result:
        returncode = 7

    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: Result())
    monkeypatch.setattr(sys, "argv", [
        "skill_dual.py", "--source", "https://github.com/owner/repo", "--skill-id", "demo-skill",
        "--acquisition-mode", "approved_unpinned", "--reinstall",
    ])
    with pytest.raises(RuntimeError, match="exit code 7"):
        module.main()
    for root in roots.values():
        assert (root / "demo-skill" / "SKILL.md").read_text(encoding="utf-8") == "old"
        assert not list(root.glob(".demo-skill.backup-*"))


def test_cross_platform_wrappers_capture_failure_and_discover_python():
    for path in (ROOT / "tools").glob("*.sh"):
        text = path.read_text(encoding="utf-8")
        assert "command -v python3" in text
        assert "set +e" in text and "CODE=$?" in text
    for path in (ROOT / "tools").glob("*.ps1"):
        text = path.read_text(encoding="utf-8")
        assert "Get-Command python3" in text
        assert "$Code=$LASTEXITCODE" in text
        assert text.index("Write-Progress", text.index("$Code=$LASTEXITCODE")) < text.index("exit $Code")


def test_agent_path_override_preserves_symlink_for_downstream_rejection(tmp_path, monkeypatch):
    agent_paths = load(ROOT / "tools" / "agent_paths.py", "agent_paths_symlink")
    security = load(ROOT / "tools" / "security_utils.py", "security_utils_agent_path")
    outside = tmp_path / "outside"
    outside.mkdir()
    link = tmp_path / "skills-link"
    link.symlink_to(outside, target_is_directory=True)
    monkeypatch.setenv("MD_AGENTS_SKILLS_DIR", str(link))
    resolved = agent_paths.resolve("agents", system="linux")
    assert resolved == link.absolute()
    with pytest.raises(ValueError, match="symlink"):
        security.ensure_no_symlink_components(resolved)


def test_installer_rollback_preserves_non_utf8_agent_file(tmp_path, monkeypatch):
    installer = load(ROOT / "install.py", "md_install_non_utf8")
    project = tmp_path / "project"
    project.mkdir()
    original = b"\xff\xfehuman-rules\x00"
    (project / "AGENTS.md").write_bytes(original)
    (project / ".gitignore").write_text("existing\n", encoding="utf-8")
    with pytest.raises(UnicodeDecodeError):
        installer.install(project)
    assert (project / "AGENTS.md").read_bytes() == original
    assert (project / ".gitignore").read_text(encoding="utf-8") == "existing\n"
    assert not (project / "prompts").exists()


def test_guidance_sync_is_transactional_and_receipt_path_is_project_relative(tmp_path, monkeypatch):
    sync = load(ROOT / "tools" / "sync_agent_guidance.py", "sync_guidance_transaction")
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("agents-human\n", encoding="utf-8")
    (project / "CLAUDE.md").write_text("claude-human\n", encoding="utf-8")
    original_write = sync.atomic_write_text
    calls = {"count": 0}

    def fail_second(path, text, *args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 2:
            raise OSError("forced second write failure")
        return original_write(path, text, *args, **kwargs)

    monkeypatch.setattr(sync, "atomic_write_text", fail_second)
    with pytest.raises(OSError, match="forced second write failure"):
        sync.sync_guidance(project, ROOT, receipt_path=".prompt_suite/receipt.json")
    assert (project / "AGENTS.md").read_text(encoding="utf-8") == "agents-human\n"
    assert (project / "CLAUDE.md").read_text(encoding="utf-8") == "claude-human\n"
    assert not (project / ".prompt_suite/receipt.json").exists()

    monkeypatch.setattr(sync, "atomic_write_text", original_write)
    result = sync.sync_guidance(project, ROOT, receipt_path=".prompt_suite/receipt.json")
    saved = json.loads((project / ".prompt_suite/receipt.json").read_text(encoding="utf-8"))
    assert saved["receipt_path"] == str((project / ".prompt_suite/receipt.json").absolute())
    assert result["receipt_path"] == saved["receipt_path"]


def test_local_skill_receipt_failure_restores_previous_installations(tmp_path, monkeypatch):
    module = load(ROOT / "tools" / "register_local_skill_dual.py", "register_receipt_rollback")
    source = tmp_path / "source"
    source.mkdir()
    (source / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")
    roots = {"agents": tmp_path / "agents", "claude-code": tmp_path / "claude", "opencode": tmp_path / "opencode"}
    for root in roots.values():
        existing = root / "demo-skill"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("old", encoding="utf-8")
    monkeypatch.setattr(module, "all_default_destinations", lambda: roots)
    monkeypatch.setattr(module, "append_event", lambda *args, **kwargs: {"log_file": "test"})
    monkeypatch.setattr(module, "atomic_write_json", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("receipt failed")))
    monkeypatch.setattr(sys, "argv", [
        "register_local_skill_dual.py", "--source-directory", str(source), "--skill-id", "demo-skill",
        "--reinstall", "--receipt-path", str(tmp_path / "receipt.json"),
    ])
    with pytest.raises(OSError, match="receipt failed"):
        module.main()
    for root in roots.values():
        assert (root / "demo-skill" / "SKILL.md").read_text(encoding="utf-8") == "old"


def test_skill_conformance_requires_exact_relative_artifact_path(tmp_path, monkeypatch):
    module = load(ROOT / "tools" / "run_skill_conformance.py", "skill_conformance_exact_path")
    fake_root = tmp_path / "suite"
    (fake_root / "evaluations/skills").mkdir(parents=True)
    (fake_root / "schemas").mkdir()
    spec = {
        "skill_id": "demo-skill",
        "lock_required": True,
        "expected_contract": {"expected_artifacts": [{
            "prompt_id": "MD-01",
            "primary": {"path": "reports/expected/result.md", "format": "markdown", "required_when_writing": True},
            "supporting": [],
        }]},
    }
    (fake_root / "evaluations/skills/demo-skill.json").write_text(json.dumps(spec), encoding="utf-8")
    (fake_root / "skills.lock.json").write_text(json.dumps({"entries": [{"skill_id": "demo-skill", "lock_status": "resolved", "commit_sha": "a" * 40}]}), encoding="utf-8")
    output = tmp_path / "output"
    (output / "wrong/location").mkdir(parents=True)
    (output / "wrong/location/result.md").write_text("wrong path", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", fake_root)
    monkeypatch.setattr(sys, "argv", ["run_skill_conformance.py", "--skill-id", "demo-skill", "--output-dir", str(output)])
    assert module.main() == 1


def test_locked_skill_source_verifies_recorded_tarball_hash(tmp_path, monkeypatch):
    module = load(ROOT / "tools" / "skill_dual.py", "skill_lock_digest")
    lock = tmp_path / "skills.lock.json"
    lock.write_text(json.dumps({"entries": [{
        "skill_id": "demo-skill",
        "repository": "https://github.com/owner/repo",
        "commit_sha": "a" * 40,
        "tarball_sha256": "b" * 64,
        "lock_status": "resolved",
        "auto_install_allowed": True,
    }]}), encoding="utf-8")
    monkeypatch.setattr(module, "github_tarball_sha256", lambda repository, commit: "c" * 64)
    with pytest.raises(ValueError, match="tarball SHA-256"):
        module._locked_source(lock, "demo-skill", "https://github.com/owner/repo")


def test_remote_skill_cli_runs_in_isolated_home_then_promotes_transactionally(tmp_path, monkeypatch):
    module = load(ROOT / "tools" / "skill_dual.py", "skill_cli_isolation")
    roots = {"agents": tmp_path / "live-agents", "claude-code": tmp_path / "live-claude", "opencode": tmp_path / "live-opencode"}
    monkeypatch.setattr(module, "all_default_destinations", lambda: roots)
    monkeypatch.setattr(module, "append_event", lambda *args, **kwargs: {"log_file": "test"})
    observed = {}

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(cmd, **kwargs):
        observed["cmd"] = cmd
        observed["env"] = kwargs["env"]
        home = Path(kwargs["env"]["HOME"])
        staged = home / ".agents/skills/demo-skill"
        staged.mkdir(parents=True)
        (staged / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")
        return Result()

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", [
        "skill_dual.py", "--source", "https://github.com/owner/repo", "--skill-id", "demo-skill",
        "--acquisition-mode", "approved_unpinned",
    ])
    assert module.main() == 0
    assert observed["env"]["npm_config_ignore_scripts"] == "true"
    assert observed["env"]["npm_config_registry"] == "https://registry.npmjs.org/"
    assert observed["cmd"].count("-a") == 1 and "cline" in observed["cmd"]
    for root in roots.values():
        assert (root / "demo-skill/SKILL.md").is_file()


def test_remote_skill_receipt_failure_restores_previous_installations(tmp_path, monkeypatch):
    module = load(ROOT / "tools" / "skill_dual.py", "skill_remote_receipt_rollback")
    roots = {"agents": tmp_path / "agents", "claude-code": tmp_path / "claude", "opencode": tmp_path / "opencode"}
    for root in roots.values():
        existing = root / "demo-skill"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("old", encoding="utf-8")
    monkeypatch.setattr(module, "all_default_destinations", lambda: roots)
    monkeypatch.setattr(module, "append_event", lambda *args, **kwargs: {"log_file": "test"})

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(cmd, **kwargs):
        staged = Path(kwargs["env"]["HOME"]) / ".agents/skills/demo-skill"
        staged.mkdir(parents=True)
        (staged / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")
        return Result()

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module, "atomic_write_json", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("receipt failed")))
    monkeypatch.setattr(sys, "argv", [
        "skill_dual.py", "--source", "https://github.com/owner/repo", "--skill-id", "demo-skill",
        "--acquisition-mode", "approved_unpinned", "--reinstall", "--receipt-path", str(tmp_path / "receipt.json"),
    ])
    with pytest.raises(OSError, match="receipt failed"):
        module.main()
    for root in roots.values():
        assert (root / "demo-skill/SKILL.md").read_text(encoding="utf-8") == "old"


def test_canonical_test_runner_disables_uncontrolled_pytest_plugin_autoload():
    text = (ROOT / "tools/run_tests.py").read_text(encoding="utf-8")
    assert "PYTEST_DISABLE_PLUGIN_AUTOLOAD" in text
    assert "MD_NO_TUI" in text


def test_canonical_test_runner_uses_bounded_per_file_execution():
    text = (ROOT / "tools/run_tests.py").read_text(encoding="utf-8")
    assert "glob('test_*.py')" in text
    assert "--per-file-timeout" in text
    assert "subprocess.TimeoutExpired" in text


def test_canonical_test_runner_uses_structured_junit_counts(tmp_path):
    module = load(ROOT / "tools/run_tests.py", "md_run_tests_junit")
    report = tmp_path / "report.xml"
    report.write_text(
        '<?xml version="1.0" encoding="utf-8"?>'
        '<testsuites tests="7" failures="1" errors="0" skipped="2">'
        '<testsuite name="pytest" tests="7" failures="1" errors="0" skipped="2" />'
        '</testsuites>',
        encoding="utf-8",
    )
    counts = module._junit_counts(report)
    assert counts == {"tests": 7, "failures": 1, "errors": 0, "skipped": 2}
    source = (ROOT / "tools/run_tests.py").read_text(encoding="utf-8")
    assert "--junitxml" in source
    assert "re.findall" not in source
