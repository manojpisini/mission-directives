from __future__ import annotations

import json
import importlib.util
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "import_prompt_library", ROOT / "tools/import_prompt_library.py"
)
IMPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORTER)


def test_imported_schema_paths_preserve_source_subdirectories():
    row = {"canonical_id": "CP-001", "schema_file": "schemas/nested/result.json"}
    assert IMPORTER._schema_path(row).as_posix().endswith(
        "schemas/imported/generic_prompt_library_v3_1/nested/result.json"
    )


def test_generic_prompt_library_import_is_complete_and_deduplicated():
    plan = json.loads(
        (ROOT / "prompt_imports/generic_prompt_library_v3_1_plan.json").read_text()
    )
    imports = plan["imports"]
    assert len(imports) == 180
    assert {row["cp_id"] for row in imports} == {
        f"CP-{index:03d}" for index in range(1, 181)
    }
    assert sum(row["disposition"] == "add" for row in imports) == 56
    assert sum(row["disposition"] == "merge" for row in imports) == 124


def test_generic_prompt_library_profiles_and_schemas_are_wired():
    provenance_path = (
        ROOT / "prompt_imports/generic_prompt_library_v3_1_provenance.json"
    )
    assert provenance_path.exists()
    provenance = json.loads(provenance_path.read_text())
    catalog = json.loads((ROOT / "catalog.json").read_text())
    imported = set()
    for prompt in catalog["prompts"]:
        profile = prompt.get("imported_profile")
        if profile:
            imported.add(profile["profile_id"])
        imported.update(row["profile_id"] for row in prompt.get("imported_profiles", []))
    assert imported == {f"CP-{index:03d}" for index in range(1, 181)}
    assert len(list((ROOT / "schemas/imported/generic_prompt_library_v3_1").glob("*.json"))) == 180
    assert provenance["source_prompt_count"] == 180
    assert provenance["added_prompt_count"] == 56
    assert provenance["merged_profile_count"] == 124


def test_reviewed_workflow_refinements_are_bound_to_their_owning_profile():
    catalog = json.loads((ROOT / "catalog.json").read_text())
    metadata_by_path = {row["canonical_path"]: row for row in catalog["prompts"]}
    refinement_pattern = re.compile(
        r'<reviewed_workflow_refinement\b(?P<attributes>[^>]*)>'
    )
    profile_pattern = re.compile(r'\bprofile="(?P<profile>CP-\d{3})"')
    owner_pattern = re.compile(r'<capability_profile\s+id="(?P<profile>CP-\d{3})"')
    refinement_count = 0

    for relative_path, metadata in metadata_by_path.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for refinement in refinement_pattern.finditer(text):
            refinement_count += 1
            profile_match = profile_pattern.search(refinement.group("attributes"))
            assert profile_match, f"{relative_path}: refinement is missing profile binding"
            profile_id = profile_match.group("profile")

            prefix = text[: refinement.start()]
            owner_matches = list(owner_pattern.finditer(prefix))
            inside_merged_profile = owner_matches and prefix.rfind(
                "<capability_profile"
            ) > prefix.rfind("</capability_profile>")
            expected_profile = (
                owner_matches[-1].group("profile")
                if inside_merged_profile
                else metadata.get("imported_profile", {}).get("profile_id")
            )
            assert profile_id == expected_profile, (
                f"{relative_path}: refinement {profile_id} is owned by "
                f"{expected_profile}"
            )

    assert refinement_count == 7


def test_capability_identity_registry_exactly_matches_catalog():
    catalog = json.loads((ROOT / "catalog.json").read_text())
    registry = json.loads(
        (ROOT / "compatibility/capability_identity_registry.json").read_text()
    )
    expected = [
        {
            "capability_id": row["capability_id"],
            "prompt_id": row["prompt_id"],
            "prompt_slug": row["prompt_slug"],
            "sequence": row["sequence"],
            "title": row["title"],
            "status": "active",
        }
        for row in catalog["prompts"]
    ]
    assert registry["capabilities"] == expected
    for identity_key in ("capability_id", "prompt_id", "prompt_slug", "sequence"):
        values = [row[identity_key] for row in registry["capabilities"]]
        assert len(values) == len(set(values)), f"duplicate {identity_key}"
