from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_mastery_manual_is_deep_and_linked():
    p = ROOT / "docs/MD_MASTERY_MANUAL.md"
    text = p.read_text(encoding="utf-8")
    assert len(text.splitlines()) >= 700
    for phrase in [
        "Template System",
        "Daily TOML Logging",
        "Cross-Platform Tooling",
        "Exact Twin",
        "Prompt Anatomy",
        "Scenario Runtime",
        "Skill Governance",
        "Evaluation and Proof",
        "Troubleshooting",
    ]:
        assert phrase in text
    assert "../README.md" in text and "TEMPLATE_SYSTEM_GUIDE.md" in text


def test_new_manuals_registered():
    idx = (ROOT / "docs/MANUALS.md").read_text(encoding="utf-8")
    for name in [
        "MD_MASTERY_MANUAL",
        "TEMPLATE_SYSTEM_GUIDE",
        "LOGGING_AND_TELEMETRY_GUIDE",
        "CROSS_PLATFORM_TOOLING_GUIDE",
        "TUI_AND_OPERATOR_EXPERIENCE_GUIDE",
        "INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE",
    ]:
        assert name in idx
