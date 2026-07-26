#!/usr/bin/env python3
"""Import a deduplicated Generic Prompt Library release in one transaction."""

from __future__ import annotations

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__, total=5)

import argparse
import dataclasses
import datetime
import hashlib
import hmac
import html
import io
import json
import re
import shutil
import tempfile
import uuid
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

import yaml
from jsonschema import Draft202012Validator

try:
    import add_prompt
    from security_utils import atomic_write_json, atomic_write_text, safe_child
except ImportError:
    from tools import add_prompt
    from tools.security_utils import atomic_write_json, atomic_write_text, safe_child


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "prompt_imports/generic_prompt_library_v3_1_plan.json"
SCHEMA_DIR = Path("schemas/imported/generic_prompt_library_v3_1")
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_MEMBER_BYTES = 2 * 1024 * 1024
CONTROL_REFS = ["MD-00", "MD-01", "MD-02", "MD-03", "MD-04"]


def _member_name(root: str, relative: str) -> str:
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise ValueError(f"Unsafe archive member path: {relative}")
    return f"{root}/{path.as_posix()}"


def _schema_path(row: dict[str, Any]) -> Path:
    source = PurePosixPath(row["schema_file"])
    if not source.parts or source.parts[0] != "schemas":
        raise ValueError(f"{row['canonical_id']}: schema must be under schemas/")
    return SCHEMA_DIR.joinpath(*source.parts[1:])


def _read_member(archive: zipfile.ZipFile, name: str) -> bytes:
    try:
        info = archive.getinfo(name)
    except KeyError as exc:
        raise ValueError(f"Archive member is missing: {name}") from exc
    if info.is_dir() or info.file_size <= 0 or info.file_size > MAX_MEMBER_BYTES:
        raise ValueError(f"Archive member has an invalid size: {name}")
    if info.flag_bits & 0x1:
        raise ValueError(f"Encrypted archive members are not supported: {name}")
    if (info.external_attr >> 16) & 0o170000 == 0o120000:
        raise ValueError(f"Symbolic links are not supported in prompt archives: {name}")
    data = archive.read(info)
    if len(data) != info.file_size:
        raise ValueError(f"Archive member changed while reading: {name}")
    return data


def _archive_inventory(source: Path) -> tuple[str, list[dict[str, Any]], dict[str, bytes], str]:
    if not source.is_file() or source.is_symlink():
        raise ValueError("Prompt library source must be a regular ZIP file")
    if source.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError(f"Prompt library ZIP exceeds {MAX_ARCHIVE_BYTES} bytes")
    archive_bytes = source.read_bytes()
    if not archive_bytes or len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise ValueError(f"Prompt library ZIP must contain 1-{MAX_ARCHIVE_BYTES} bytes")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Archive contains duplicate member names")
        if sum(info.file_size for info in archive.infolist()) > MAX_ARCHIVE_BYTES:
            raise ValueError("Archive uncompressed content exceeds the safety limit")
        roots = {
            name[: -len("/catalog/canonical-prompts.json")]
            for name in names
            if name.endswith("/catalog/canonical-prompts.json")
        }
        if len(roots) != 1:
            raise ValueError("Archive must contain one canonical prompt catalog")
        library_root = roots.pop()
        checksums_text = _read_member(
            archive, f"{library_root}/CHECKSUMS.sha256"
        ).decode("utf-8")
        checksums = {}
        for line in checksums_text.splitlines():
            digest, relative = line.split(maxsplit=1)
            checksums[relative.removeprefix("./")] = digest
        catalog_path = "catalog/canonical-prompts.json"
        catalog_bytes = _read_member(archive, _member_name(library_root, catalog_path))
        rows = json.loads(catalog_bytes)
        if not isinstance(rows, list) or not rows:
            raise ValueError("Canonical prompt catalog must be a non-empty list")
        members: dict[str, bytes] = {catalog_path: catalog_bytes}
        seen_ids = set()
        for row in rows:
            cp_id = row.get("canonical_id")
            if not isinstance(cp_id, str) or not re.fullmatch(r"CP-[0-9]{3}", cp_id):
                raise ValueError(f"Invalid canonical prompt ID: {cp_id}")
            if cp_id in seen_ids:
                raise ValueError(f"Duplicate canonical prompt ID: {cp_id}")
            seen_ids.add(cp_id)
            for field in ("prompt_file", "schema_file"):
                relative = row.get(field)
                if not isinstance(relative, str):
                    raise ValueError(f"{cp_id}: missing {field}")
                members[relative] = _read_member(
                    archive, _member_name(library_root, relative)
                )
        for relative, data in members.items():
            expected = checksums.get(relative)
            actual = hashlib.sha256(data).hexdigest()
            if expected != actual:
                raise ValueError(f"Archive checksum mismatch: {relative}")
    return library_root, rows, members, hashlib.sha256(archive_bytes).hexdigest()


def _load_plan(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_MEMBER_BYTES:
        raise ValueError("Import plan must be a bounded regular JSON file")
    plan = json.loads(path.read_text(encoding="utf-8"))
    imports = plan.get("imports")
    if not isinstance(imports, list):
        raise ValueError("Import plan must contain an imports list")
    by_id = {row["canonical_id"]: row for row in rows}
    planned = {row.get("cp_id"): row for row in imports}
    if len(planned) != len(imports) or set(planned) != set(by_id):
        raise ValueError("Import plan must cover every canonical prompt exactly once")
    for cp_id, item in planned.items():
        source = by_id[cp_id]
        if item.get("title") != source.get("title"):
            raise ValueError(f"{cp_id}: plan title does not match the archive")
        disposition = item.get("disposition")
        target = item.get("target_md_id")
        if disposition not in {"add", "merge"}:
            raise ValueError(f"{cp_id}: invalid disposition")
        if disposition == "add" and target is not None:
            raise ValueError(f"{cp_id}: additions cannot declare a merge target")
        if disposition == "merge" and not re.fullmatch(r"MD-[0-9]{2,3}", target or ""):
            raise ValueError(f"{cp_id}: merge target is invalid")
        if item.get("risk") not in add_prompt.VALID_RISKS:
            raise ValueError(f"{cp_id}: risk classification is invalid")
    return plan


def _preview(
    root: Path,
    source: Path,
    plan_path: Path,
    *,
    run_full_tests: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, bytes], dict[str, Any]]:
    library_root, rows, members, archive_sha256 = _archive_inventory(source)
    plan = _load_plan(plan_path, rows)
    imports = plan["imports"]
    known_ids = {row["prompt_id"] for row in add_prompt._prompt_rows(root)}
    unknown_targets = sorted(
        {row["target_md_id"] for row in imports if row["disposition"] == "merge"}
        - known_ids
    )
    if unknown_targets:
        raise ValueError(f"Import plan has unknown merge targets: {unknown_targets}")
    start = add_prompt.next_prompt_identity(root)[1]
    additions = [row for row in imports if row["disposition"] == "add"]
    merge_targets = sorted(
        {row["target_md_id"] for row in imports if row["disposition"] == "merge"}
    )
    catalog_by_id = {row["prompt_id"]: row for row in add_prompt._prompt_rows(root)}
    merge_base = hashlib.sha256()
    for relative in ("catalog.json", "SCENARIO_CATALOG.json", "config/department_packs.json"):
        merge_base.update(relative.encode())
        merge_base.update((root / relative).read_bytes())
    for prompt_id in merge_targets:
        relative = catalog_by_id[prompt_id]["canonical_path"]
        merge_base.update(relative.encode())
        merge_base.update((root / relative).read_bytes())
    assigned = {
        row["cp_id"]: f"MD-{start + index}" for index, row in enumerate(additions)
    }
    preview: dict[str, Any] = {
        "status": "dry_run",
        "suite_version": (root / "VERSION").read_text(encoding="utf-8").strip(),
        "library": plan.get("library"),
        "library_version": plan.get("version"),
        "library_root": library_root,
        "archive_sha256": archive_sha256,
        "plan_sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        "catalog_sha256": hashlib.sha256((root / "catalog.json").read_bytes()).hexdigest(),
        "source_prompt_count": len(rows),
        "add_count": len(additions),
        "merge_count": len(imports) - len(additions),
        "assigned_prompt_ids": assigned,
        "schema_count": len(rows),
        "run_full_tests": run_full_tests,
        "merge_base_sha256": merge_base.hexdigest(),
    }
    canonical = json.dumps(preview, sort_keys=True, separators=(",", ":")).encode()
    preview["approval_token"] = hashlib.sha256(canonical).hexdigest()
    return preview, rows, members, plan


def _render_prompt(metadata: dict[str, Any], body: str) -> str:
    frontmatter = yaml.dump(
        metadata,
        Dumper=add_prompt._NoAliasDumper,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    ).strip()
    return f"---\n{frontmatter}\n---\n\n{body.strip()}\n"


def _source_body(row: dict[str, Any], members: dict[str, bytes], schema_path: str) -> tuple[str, str]:
    source_bytes = members[row["prompt_file"]]
    try:
        source_text = source_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{row['canonical_id']}: prompt is not UTF-8") from exc
    body = add_prompt._split_source(source_text.replace("\r\n", "\n"))
    body = body.replace(row["schema_file"], schema_path)
    return source_text, body


def _merge_profiles(
    root: Path,
    rows_by_id: dict[str, dict[str, Any]],
    members: dict[str, bytes],
    merge_rows: list[dict[str, Any]],
) -> None:
    catalog_rows = {row["prompt_id"]: row for row in add_prompt._prompt_rows(root)}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in merge_rows:
        grouped[item["target_md_id"]].append(item)
    scenario_path = root / "SCENARIO_CATALOG.json"
    scenarios = json.loads(scenario_path.read_text(encoding="utf-8"))
    atomic_by_prompt = {
        row["prompts"][0]: row
        for row in scenarios.get("atomic_scenarios", [])
        if len(row.get("prompts", [])) == 1
    }
    for target_id, items in grouped.items():
        path = root / catalog_rows[target_id]["canonical_path"]
        text = path.read_text(encoding="utf-8")
        _, frontmatter, body = text.split("---", 2)
        metadata = yaml.safe_load(frontmatter)
        aliases = list(metadata.get("aliases") or [])
        imported = list(metadata.get("imported_profiles") or [])
        blocks = []
        for item in sorted(items, key=lambda value: value["cp_id"]):
            row = rows_by_id[item["cp_id"]]
            schema_path = _schema_path(row).as_posix()
            source_text, source_body = _source_body(row, members, schema_path)
            routes = list(dict.fromkeys([row["title"], *(row.get("routes") or [])]))
            aliases.extend(routes)
            imported.append(
                {
                    "profile_id": item["cp_id"],
                    "title": row["title"],
                    "source_library": "generic-prompt-library",
                    "source_version": "3.1.0",
                    "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
                    "schema_path": schema_path,
                }
            )
            blocks.append(
                f'<capability_profile id="{item["cp_id"]}" title="{html.escape(row["title"], quote=True)}" '
                f'schema="{schema_path}">\n<source_prompt format="markdown" encoding="xml-escaped">\n'
                f"{html.escape(source_body, quote=False)}\n</source_prompt>\n</capability_profile>"
            )
        if len({row["profile_id"] for row in imported}) != len(imported):
            raise ValueError(f"{target_id}: imported profile already exists")
        metadata["aliases"] = list(dict.fromkeys(aliases))
        metadata["imported_profiles"] = imported
        profile_section = (
            "\n<imported_capability_profiles source=\"generic-prompt-library\" version=\"3.1.0\">\n"
            "Select only the profile that matches the routed request; preserve the parent prompt's authority and verification contracts.\n\n"
            + "\n\n".join(blocks)
            + "\n</imported_capability_profiles>\n"
        )
        marker = "\n</prompt>"
        if marker not in body:
            raise ValueError(f"{target_id}: canonical prompt closing marker is missing")
        body = body.rsplit(marker, 1)[0].rstrip() + profile_section + marker
        words = len(re.findall(r"\b\w+[\w-]*\b", body))
        budget = metadata.setdefault("complexity_budget", {})
        budget["maximum_body_words"] = max(int(budget.get("maximum_body_words", 0)), words + 100)
        budget["maximum_body_lines"] = max(
            int(budget.get("maximum_body_lines", 0)), len(body.splitlines()) + 20
        )
        atomic_write_text(path, _render_prompt(metadata, body))
        atomic = atomic_by_prompt[target_id]
        atomic["aliases"] = metadata["aliases"]
        atomic["imported_profiles"] = [row["profile_id"] for row in imported]
    atomic_write_json(scenario_path, scenarios)


def _prepared_addition(
    root: Path,
    row: dict[str, Any],
    item: dict[str, Any],
    members: dict[str, bytes],
    source_dir: Path,
) -> add_prompt.PreparedPrompt:
    schema_path = _schema_path(row).as_posix()
    source_text, source_body = _source_body(row, members, schema_path)
    source_path = source_dir / f"{item['cp_id'].lower()}.md"
    atomic_write_text(source_path, source_body + "\n")
    prepared = add_prompt.prepare_prompt(
        root,
        source=source_path,
        title=row["title"],
        category=row["domain"].replace("-and-", "_and_").replace("-", "_"),
        prompt_role="operational",
        prompt_type="operational",
        risk_level=item["risk"],
        allowed_modes=("DRAFT_ONLY", "APPLY_SAFE", "VERIFY_ONLY"),
        requires=CONTROL_REFS,
    )
    metadata = prepared.metadata
    metadata["description"] = row["purpose"]
    metadata["aliases"] = list(dict.fromkeys([row["title"], *(row.get("routes") or [])]))
    metadata["machine_output_schema"] = schema_path
    metadata["imported_profile"] = {
        "profile_id": item["cp_id"],
        "source_library": "generic-prompt-library",
        "source_version": "3.1.0",
        "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
    }
    body = prepared.content.split("---", 2)[2]
    content = _render_prompt(metadata, body)
    return dataclasses.replace(prepared, metadata=metadata, content=content)


def _write_schemas(root: Path, rows: list[dict[str, Any]], members: dict[str, bytes]) -> None:
    target = root / SCHEMA_DIR
    target.mkdir(parents=True, exist_ok=False)
    destinations = [_schema_path(row) for row in rows]
    if len(destinations) != len(set(destinations)):
        raise ValueError("Canonical prompt schemas must have unique destination paths")
    for row in rows:
        schema = json.loads(members[row["schema_file"]])
        Draft202012Validator.check_schema(schema)
        destination = root / _schema_path(row)
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(destination, schema)


def _append_staged_catalog(root: Path, prepared: add_prompt.PreparedPrompt) -> None:
    path = root / "catalog.json"
    catalog = json.loads(path.read_text(encoding="utf-8"))
    catalog["prompts"].append(prepared.metadata)
    catalog["prompts"].sort(key=lambda row: row["sequence"])
    catalog["prompt_count"] = len(catalog["prompts"])
    atomic_write_json(path, catalog)


def _update_department_packs(root: Path, added: list[add_prompt.PreparedPrompt]) -> None:
    path = root / "config/department_packs.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    grouped: dict[str, list[str]] = defaultdict(list)
    for prompt in added:
        pack = prompt.metadata["category"].upper()
        grouped[pack].append(prompt.prompt_id)
    for pack, prompt_ids in grouped.items():
        existing = data["department_packs"].get(pack, [])
        values = list(dict.fromkeys(CONTROL_REFS + existing + prompt_ids))
        data["department_packs"][pack] = sorted(
            values, key=lambda value: int(value.split("-")[1])
        )
    atomic_write_json(path, data)


def _apply_import(
    root: Path,
    source: Path,
    plan_path: Path,
    preview: dict[str, Any],
    rows: list[dict[str, Any]],
    members: dict[str, bytes],
    plan: dict[str, Any],
    *,
    run_full_tests: bool,
) -> dict[str, Any]:
    baseline = add_prompt._manifest_files(root)
    rows_by_id = {row["canonical_id"]: row for row in rows}
    with tempfile.TemporaryDirectory(prefix="md-library-import-") as tmp:
        staged = Path(tmp) / "suite"
        shutil.copytree(root, staged, ignore=add_prompt._copy_ignore_factory(root), symlinks=True)
        _write_schemas(staged, rows, members)
        merge_rows = [row for row in plan["imports"] if row["disposition"] == "merge"]
        _merge_profiles(staged, rows_by_id, members, merge_rows)
        source_dir = staged / ".prompt_suite/runtime/prompt-library-import"
        source_dir.mkdir(parents=True, exist_ok=True)
        added = []
        for item in [row for row in plan["imports"] if row["disposition"] == "add"]:
            prepared = _prepared_addition(staged, rows_by_id[item["cp_id"]], item, members, source_dir)
            add_prompt._write_prompt_and_fixtures(staged, prepared)
            add_prompt._update_registry_routes(staged, prepared, ())
            _append_staged_catalog(staged, prepared)
            added.append(prepared)
        _update_department_packs(staged, added)
        provenance = {
            "suite_version": (staged / "VERSION").read_text(encoding="utf-8").strip(),
            "library": plan.get("library"),
            "library_version": plan.get("version"),
            "archive_sha256": preview["archive_sha256"],
            "plan_sha256": preview["plan_sha256"],
            "source_prompt_count": len(rows),
            "added_prompt_count": len(added),
            "merged_profile_count": len(merge_rows),
            "schema_count": len(rows),
            "added_prompt_ids": [row.prompt_id for row in added],
            "merged_target_ids": sorted({row["target_md_id"] for row in merge_rows}),
        }
        atomic_write_json(
            staged / "prompt_imports/generic_prompt_library_v3_1_provenance.json",
            provenance,
        )
        add_prompt.validate_staged_suite(staged, run_full_tests=run_full_tests)
        lock = root / ".prompt_suite/prompt-library-import.lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        with add_prompt.exclusive_lock(lock):
            changed = add_prompt._promote_verified_diff(root, staged, baseline)
    receipt = {
        **provenance,
        "status": "pass",
        "changed_files": changed,
        "full_tests_run": run_full_tests,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    receipt_path = root / ".prompt_suite/results/prompt-library-import" / f"generic-v3_1-{uuid.uuid4().hex[:12]}.json"
    try:
        atomic_write_json(receipt_path, receipt, default_mode=0o600)
    except Exception:
        add_prompt._restore_promoted_paths(root, baseline, changed)
        raise
    receipt["receipt_path"] = receipt_path.relative_to(root).as_posix()
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--approval-token")
    parser.add_argument("--skip-full-tests", action="store_true")
    args = parser.parse_args()
    try:
        preview, rows, members, plan = _preview(
            ROOT,
            args.source,
            args.plan,
            run_full_tests=not args.skip_full_tests,
        )
        if args.dry_run:
            print(json.dumps(preview, indent=2))
            return 0
        token = args.approval_token or ""
        if not re.fullmatch(r"[0-9a-f]{64}", token) or not hmac.compare_digest(token, preview["approval_token"]):
            raise ValueError("Prompt library import requires the exact token from a current dry run")
        result = _apply_import(
            ROOT,
            args.source,
            args.plan,
            preview,
            rows,
            members,
            plan,
            run_full_tests=not args.skip_full_tests,
        )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        if "_MD_TUI" in globals() and hasattr(_MD_TUI, "fail"):
            _MD_TUI.fail(exc)
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
