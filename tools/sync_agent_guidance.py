#!/usr/bin/env python3
"""Create or synchronize a managed MD guidance block in root agent files.

The tool never overwrites unmanaged instructions. It creates missing files,
replaces only the block between its managed markers, supports dry-run and
removal, and records a machine-readable receipt when requested.
"""

from __future__ import annotations

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)


import argparse
import datetime as dt
import difflib
import json
import os
from pathlib import Path
from typing import Iterable

try:
    from security_utils import (
        atomic_write_bytes,
        atomic_write_text,
        ensure_no_symlink_components,
        safe_child,
        is_within,
    )
except ImportError:
    from tools.security_utils import (
        atomic_write_bytes,
        atomic_write_text,
        ensure_no_symlink_components,
        safe_child,
        is_within,
    )

SUITE_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = SUITE_ROOT / "policies/agent_guidance_policy.json"
BEGIN_MARKER = "<!-- BEGIN MD MANAGED GUIDANCE -->"
END_MARKER = "<!-- END MD MANAGED GUIDANCE -->"
FALLBACK_DEFAULT_AGENT_FILES = ["AGENTS.md", "CLAUDE.md"]
SUPPORTED_AGENT_FILES = frozenset(FALLBACK_DEFAULT_AGENT_FILES)


def load_policy(suite_root: Path = SUITE_ROOT) -> dict:
    path = suite_root / "policies/agent_guidance_policy.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "keyword": "MD",
        "default_agent_files": FALLBACK_DEFAULT_AGENT_FILES,
        "shortcut_routes": [],
    }


_POLICY = load_policy()
DEFAULT_AGENT_FILES = list(
    _POLICY.get("default_agent_files") or FALLBACK_DEFAULT_AGENT_FILES
)


def _safe_relative_path(project_root: Path, suite_root: Path) -> str:
    try:
        rel = os.path.relpath(suite_root.resolve(), project_root.resolve())
        return "." if rel == "." else Path(rel).as_posix()
    except ValueError:  # Different Windows drives.
        return suite_root.resolve().as_posix()


def _join(base: str, child: str) -> str:
    if base == ".":
        return child
    return f"{base.rstrip('/')}/{child}"


def _quote_command_path(path: str) -> str:
    return f'"{path}"' if any(ch.isspace() for ch in path) else path


def _validate_agent_files(agent_files: Iterable[str]) -> list[str]:
    result: list[str] = []
    for raw in agent_files:
        normalized = raw.replace("\\", "/").strip()
        candidate = Path(normalized)
        if not normalized or candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(
                f"Agent file must be a safe project-relative path: {raw!r}"
            )
        if candidate.suffix.lower() != ".md":
            raise ValueError(f"Agent guidance target must be Markdown: {raw!r}")
        value = candidate.as_posix()
        if value not in SUPPORTED_AGENT_FILES:
            raise ValueError(
                f"Unsupported agent guidance target {raw!r}; only AGENTS.md and CLAUDE.md are managed"
            )
        if value not in result:
            result.append(value)
    return result


def _shortcut_table(policy: dict) -> str:
    rows = policy.get("shortcut_routes") or []
    if not rows:
        return "| Keyword | Route | Purpose |\n|---|---|---|\n| `MD <terms>` | keyword lookup | find the smallest relevant route |"
    lines = ["| Keyword after `MD` | Preferred route | Purpose |", "|---|---|---|"]
    for row in rows:
        lines.append(f"| `{row['keyword']}` | `{row['target']}` | {row['purpose']} |")
    return "\n".join(lines)


def render_guidance(
    project_root: Path | str,
    suite_root: Path | str = SUITE_ROOT,
    agent_file: str = "AGENTS.md",
) -> str:
    project_root = Path(project_root).resolve()
    suite_root = Path(suite_root).resolve()
    policy = load_policy(suite_root)
    suite_rel = _safe_relative_path(project_root, suite_root)
    version = (
        (suite_root / "VERSION").read_text(encoding="utf-8").strip()
        if (suite_root / "VERSION").exists()
        else "unknown"
    )
    md_py = _quote_command_path(_join(suite_rel, "tools/md.py"))
    sync_py = _quote_command_path(_join(suite_rel, "tools/sync_agent_guidance.py"))
    add_prompt_py = _quote_command_path(_join(suite_rel, "tools/add_prompt.py"))
    cleanup_py = _quote_command_path(_join(suite_rel, "tools/cleanup.py"))
    prompts_path = _join(suite_rel, "prompts/")
    catalog_path = _join(suite_rel, "catalog.json")
    scenarios_path = _join(suite_rel, "SCENARIO_CATALOG.json")
    execution_path = _join(suite_rel, "PROMPT_EXECUTION_ORDER.md")
    skill_registry_path = _join(suite_rel, "skill_registry.json")
    policy_path = _join(suite_rel, "policies/auto_prompt_policy.json")
    loop_policy_path = _join(suite_rel, "policies/loop_execution_policy.json")
    blocks = [
        BEGIN_MARKER,
        "## MD prompt routing and productivity guidance",
        "",
        f"This managed section connects **{agent_file}** to Mission Directives **{version}** at `{suite_rel}`. Preserve instructions outside this block. Regenerate this block with `python {sync_py} --project-root .` instead of editing it manually.",
        "",
        "**Scope note:** Only AGENTS.md and CLAUDE.md are managed. Other agent instruction filenames are intentionally excluded.",
        "",
        "### When to invoke MD",
        "",
        "- Treat the standalone keyword `MD` as an explicit request to use this suite.",
        "- If the user supplies an exact `MD-###` or `C-###`, inspect that target with `explain` before execution.",
        "- If `MD` is followed by ordinary words, treat those words as a lookup query. Do not guess a prompt ID from memory.",
        "- Even without the keyword, use MD when the request clearly benefits from its evidence, authorization, skill, loop, artifact, or verification contracts.",
        "- Use `MD-191` only for ambiguities whose answers change routing, authority, evidence lane, output medium, budget, or acceptance criteria. Do not interrogate the user about details that can be safely inferred or deferred.",
        "",
        "### Fast lookup workflow",
        "",
        "```bash",
        f'python {md_py} lookup "<user terms>" --limit 8',
        f"python {md_py} explain <MD-ID|C-ID|DEPARTMENT_PACK>",
        f"python {md_py} plan <target> --mode <MODE> --root . --dry-run",
        "```",
        "",
        "Lookup before opening many prompt files. Prefer the highest-confidence exact prompt or composite scenario. If results remain ambiguous, ask one route-changing question, then rerun lookup.",
        "",
        "### Productivity shortcuts",
        "",
        _shortcut_table(policy),
        "",
        "These shortcuts are defaults, not blind dispatch rules. Confirm that the route owns the requested outcome and that its authority and evidence assumptions fit.",
        "",
        "### Adding a prompt",
        "",
        "- Use `MD-199` when the prompt needs overlap analysis, refinement, routing decisions, or agentic review.",
        f'- Use `python {add_prompt_py} --source <file.md> --title "<title>"` for a deterministic transactional addition.',
        "- Never copy a prompt into the prompts directory manually; the catalog, identity registry, graph, templates, skills, fixtures, evaluations, tests, validation, and manifest must remain synchronized.",
        "",
        "### Canonical lookup order",
        "",
        f'1. Run `python {md_py} lookup "<terms>"`.',
        f"2. Inspect the selected route with `python {md_py} explain <target>`.",
        f"3. Use `{catalog_path}` for prompt metadata and `{scenarios_path}` for composite workflows.",
        f"4. Use `{execution_path}` for phase order, modes, branches, locks, and completion semantics.",
        f"5. Load only the selected bodies from `{prompts_path}` plus their declared prerequisites.",
        f"6. Consult schemas, policies, `{skill_registry_path}`, `{policy_path}`, and `{loop_policy_path}` only when triggered.",
        "",
        "### Efficiency and anti-bloat rules",
        "",
        "- Select the **smallest coherent graph** that owns the observable outcome.",
        "- **Do not load every prompt**, every department pack entry, or every skill into context.",
        "- Load the five control prompts once per run, then only selected capabilities and required handoffs.",
        "- Prefer a composite scenario when it already expresses the complete workflow; otherwise start from one primary prompt.",
        "- Invoke a skill through `MD-192` and `MD-196` only when its genuine capability is needed. Installed does not mean required.",
        "- Discover, install, or create a skill through `MD-193` to `MD-195` only when native execution cannot satisfy the acceptance criteria cleanly.",
        "- Loop through `MD-197` and `MD-198` only for a finite queue or measurable improvement. Stop on verified success, plateau, budget exhaustion, stale evidence, lost authority, or human stop.",
        "- Keep skill output quarantined until the routed verification step accepts the exact artifact.",
        "- Route code-native illustrations, vectors, infographics, diagrams, and presentation assets through the exact local `visual-assets` skill when genuinely required; route Strudel music code through `strudel`.",
        "- Do not imply publication, sending, submission, deployment, merging, purchasing, or other external action from a draft or plan.",
        "- For every genuine planning/execution pair, present the completed plan for user review, incorporate requested changes, re-verify and re-freeze it, request review again, then ask for explicit consent to invoke only the exact execution twin declared in `paired_prompt_id`. Never substitute another executor or infer consent from the original task.",
        "",
        "### Paired plan review workflow",
        "",
        f"- Inspect the exact reciprocal twin with `python {md_py} pair-status <PLANNING-MD-ID> --handoff-ready --review-status approved`.",
        "- Requested changes invalidate prior approval and consent; revise, re-freeze under a new hash, and request review again.",
        "- Execute only after the user approves the final frozen plan and explicitly consents to the named exact execution twin.",
        "",
        "### Project cleanup",
        "",
        f"- Preview removal with `python {cleanup_py} . --dry-run`.",
        f"- Run approved cleanup with `python {cleanup_py} . --yes` or a reviewed approval token.",
        "- Cleanup removes only validated Mission Directives-managed paths and text blocks; preserve unrelated project content and nonempty docs.",
        "",
        "### Core locations",
        "",
        f"- Prompt bodies: `{prompts_path}`",
        f"- Prompt catalog: `{catalog_path}`",
        f"- Scenario catalog: `{scenarios_path}`",
        f"- Execution guide: `{execution_path}`",
        f"- Skill registry: `{skill_registry_path}`",
        f"- CLI: `{_join(suite_rel, 'tools/md.py')}`",
        f"- Manuals: `{_join(suite_rel, 'MANUALS.md')}` and `{_join(suite_rel, 'docs/')}`",
        "",
        "### Honest completion",
        "",
        "A route is not complete merely because a prompt or skill ran. Completion requires the selected prompt's task-specific criteria, `=VERIFY:{id}` evidence, explicit unknowns and residuals, and the applicable human approval or external-action gate.",
        END_MARKER,
    ]
    return "\n".join(blocks) + "\n"


def _detect_newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def _strip_managed_block(text: str) -> tuple[str, bool]:
    begin_count = text.count(BEGIN_MARKER)
    end_count = text.count(END_MARKER)
    if begin_count != end_count:
        raise ValueError("Malformed MD managed block: unmatched begin/end marker")
    if begin_count > 1:
        raise ValueError("Malformed MD managed block: duplicate managed blocks")
    if begin_count == 0:
        return text, False
    start = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER, start) + len(END_MARKER)
    before = text[:start]
    after = text[end:]
    if before.endswith("\r\n\r\n") and after.startswith("\r\n"):
        after = after[2:]
    elif before.endswith("\n\n") and after.startswith("\n"):
        after = after[1:]
    return before + after, True


def _merge_block(existing: str, block: str) -> str:
    newline = _detect_newline(existing)
    clean, had_block = _strip_managed_block(existing)
    normalized_block = block.replace("\n", newline)
    if had_block:
        # Reinsert at the old block location by locating the clean prefix length.
        original_start = existing.index(BEGIN_MARKER)
        prefix = existing[:original_start]
        original_end = existing.index(END_MARKER, original_start) + len(END_MARKER)
        suffix = existing[original_end:]
        return prefix + normalized_block.rstrip("\r\n") + suffix
    if not clean:
        return normalized_block
    separator = (
        ""
        if clean.endswith(newline * 2)
        else newline
        if clean.endswith(newline)
        else newline * 2
    )
    return clean + separator + normalized_block


def _atomic_write(path: Path, text: str) -> None:
    atomic_write_text(path, text)


def _snapshot_path(path: Path) -> tuple[bytes | None, int | None]:
    ensure_no_symlink_components(path)
    if not path.exists():
        return None, None
    if not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")
    return path.read_bytes(), path.stat().st_mode & 0o7777


def _restore_path(path: Path, snapshot: tuple[bytes | None, int | None]) -> None:
    data, mode = snapshot
    ensure_no_symlink_components(path)
    if data is None:
        path.unlink(missing_ok=True)
        return
    atomic_write_bytes(path, data)
    if mode is not None:
        try:
            os.chmod(path, mode)
        except OSError:
            pass


def sync_guidance(
    project_root: Path | str,
    suite_root: Path | str = SUITE_ROOT,
    agent_files: Iterable[str] | None = None,
    *,
    dry_run: bool = False,
    remove: bool = False,
    receipt_path: Path | str | None = None,
    show_diff: bool = False,
) -> dict:
    project_root = ensure_no_symlink_components(Path(project_root).expanduser())
    suite_root = ensure_no_symlink_components(Path(suite_root).expanduser())
    if not project_root.exists():
        project_root.mkdir(parents=True)
    ensure_no_symlink_components(project_root)
    if not project_root.is_dir():
        raise ValueError(f"Project root is not a directory: {project_root}")
    for required in ["catalog.json", "SCENARIO_CATALOG.json", "prompts", "tools"]:
        required_path = suite_root / required
        ensure_no_symlink_components(required_path)
        if not required_path.exists():
            raise ValueError(f"Suite root is missing required path: {required}")

    files = _validate_agent_files(
        agent_files
        or load_policy(suite_root).get("default_agent_files")
        or DEFAULT_AGENT_FILES
    )
    target_paths = {name: safe_child(project_root, name) for name in files}
    for path in target_paths.values():
        ensure_no_symlink_components(path)
        if path.exists() and not path.is_file():
            raise ValueError(f"Agent guidance target is not a regular file: {path}")

    rp: Path | None = None
    if receipt_path:
        raw_receipt = Path(receipt_path).expanduser()
        if raw_receipt.is_absolute():
            rp = ensure_no_symlink_components(raw_receipt)
            if not is_within(rp, project_root):
                raise ValueError("Receipt path must remain inside the project root")
        else:
            rp = safe_child(project_root, raw_receipt)
        ensure_no_symlink_components(rp)
        if rp in target_paths.values():
            raise ValueError("Receipt path must not overwrite AGENTS.md or CLAUDE.md")
        if rp.exists() and not rp.is_file():
            raise ValueError(f"Receipt target is not a regular file: {rp}")

    changed: list[str] = []
    created: list[str] = []
    updated: list[str] = []
    removed: list[str] = []
    unchanged: list[str] = []
    diffs: dict[str, str] = {}
    desired_by_name: dict[str, str] = {}
    existing_by_name: dict[str, str] = {}

    # Compute every mutation before writing any file. This ensures malformed
    # content or an invalid route cannot leave a partially synchronized pair.
    for name, path in target_paths.items():
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        existing_by_name[name] = existing
        if remove:
            desired, had = _strip_managed_block(existing)
            if had:
                desired = desired.rstrip("\r\n") + ("\n" if desired.strip() else "")
                removed.append(name)
        else:
            desired = _merge_block(
                existing, render_guidance(project_root, suite_root, name)
            )
        desired_by_name[name] = desired
        if desired == existing:
            unchanged.append(name)
            continue
        changed.append(name)
        (updated if path.exists() else created).append(name)
        if show_diff:
            diffs[name] = "".join(
                difflib.unified_diff(
                    existing.splitlines(keepends=True),
                    desired.splitlines(keepends=True),
                    fromfile=f"a/{name}",
                    tofile=f"b/{name}",
                )
            )

    status = (
        ("dry_run_changes" if changed else "dry_run_unchanged")
        if dry_run
        else ("changed" if changed else "unchanged")
    )
    receipt = {
        "schema_version": "1.0",
        "status": status,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "project_root": project_root.as_posix(),
        "suite_root": suite_root.as_posix(),
        "suite_version": (suite_root / "VERSION").read_text(encoding="utf-8").strip()
        if (suite_root / "VERSION").exists()
        else "unknown",
        "managed_files": files,
        "changed_files": changed,
        "created_files": created,
        "updated_files": updated,
        "removed_blocks": removed,
        "unchanged_files": unchanged,
        "dry_run": dry_run,
        "remove": remove,
        "diffs": diffs if show_diff else {},
        "receipt_path": rp.as_posix() if rp else None,
    }
    if dry_run:
        return receipt

    snapshots = {path: _snapshot_path(path) for path in target_paths.values()}
    if rp is not None:
        snapshots[rp] = _snapshot_path(rp)
    try:
        for name in changed:
            _atomic_write(target_paths[name], desired_by_name[name])
        if rp is not None:
            _atomic_write(rp, json.dumps(receipt, indent=2) + "\n")
    except Exception:
        for path, snapshot in snapshots.items():
            _restore_path(path, snapshot)
        raise
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--suite-root", default=str(SUITE_ROOT))
    parser.add_argument("--agent-file", action="append", dest="agent_files")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--show-diff", action="store_true")
    parser.add_argument(
        "--receipt", default=".prompt_suite/agent-guidance-receipt.json"
    )
    parser.add_argument("--print-block", action="store_true")
    args = parser.parse_args()
    suite_root = Path(args.suite_root)
    files = args.agent_files
    try:
        if args.print_block:
            print(
                render_guidance(
                    args.project_root, suite_root, (files or DEFAULT_AGENT_FILES)[0]
                )
            )
            return 0
        receipt = sync_guidance(
            args.project_root,
            suite_root,
            files,
            dry_run=args.dry_run,
            remove=args.remove,
            receipt_path=args.receipt if args.receipt else None,
            show_diff=args.show_diff,
        )
        print(json.dumps(receipt, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
