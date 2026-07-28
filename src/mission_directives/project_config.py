from __future__ import annotations

import copy
import json
import os
import re
import tempfile
import tomllib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

CONFIG_DIRNAME = ".mission-directives"
CONFIG_FILENAME = "project.json"
SCHEMA_FILENAME = "project_context.schema.json"
SCHEMA_VERSION = "3"
MAX_MANIFEST_BYTES = 1_048_576
MAX_DETECTION_DIRS = 64
TOP_LEVEL_SECTIONS = (
    "schema_version",
    "revision",
    "project",
    "goals",
    "scope",
    "stack",
    "paths",
    "commands",
    "constraints",
    "working_agreements",
    "current_state",
    "provenance",
    "extensions",
)

SENSITIVE_KEY_RE = re.compile(
    r"(?i)(secret|token|password|passwd|api[-_]?key|private[-_]?key|client[-_]?secret|credential|access[-_]?key)"
)
SENSITIVE_VALUE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9._-]{10,}\.[a-zA-Z0-9._-]{10,}\b"),
)

LANGUAGE_BY_ECOSYSTEM = {
    "go": "Go",
    "java": "Java",
    "node": "JavaScript",
    "php": "PHP",
    "python": "Python",
    "ruby": "Ruby",
    "rust": "Rust",
}

FRAMEWORK_HINTS = {
    "actix-web": "Actix Web",
    "astro": "Astro",
    "axum": "Axum",
    "django": "Django",
    "express": "Express",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "gin": "Gin",
    "next": "Next.js",
    "nestjs": "NestJS",
    "react": "React",
    "rocket": "Rocket",
    "svelte": "Svelte",
    "spring-boot-starter": "Spring Boot",
    "vue": "Vue",
}

DATABASE_HINTS = {
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "postgres": "PostgreSQL",
    "psycopg": "PostgreSQL",
    "redis": "Redis",
    "sqlite": "SQLite",
}

SERVICE_HINTS = {
    "docker": "Docker",
    "kafka": "Kafka",
    "rabbitmq": "RabbitMQ",
}

DEPLOYMENT_HINTS = {
    "aws-cdk": "AWS",
    "cloudflare": "Cloudflare",
    "firebase": "Firebase",
    "fly": "Fly.io",
    "netlify": "Netlify",
    "vercel": "Vercel",
}

DERIVED_PROJECT_FIELDS = {"name", "summary"}
PRESERVED_REFRESH_FIELDS = {
    "project.mission",
    "project.owners",
    "goals",
    "scope",
    "constraints",
}


class ProjectConfigError(ValueError):
    """Base error for project config operations."""


class ProjectConfigValidationError(ProjectConfigError):
    """Raised when a project config does not match the contract."""


class ProjectConfigSecretError(ProjectConfigValidationError):
    """Raised when a project config contains secret-bearing data."""


class ProjectConfigNotFoundError(ProjectConfigError, FileNotFoundError):
    """Raised when the project config file does not exist."""


class StaleProjectConfigError(ProjectConfigError):
    """Raised when a caller tries to save against an outdated revision."""


def seed_project_config(project_root: str | Path) -> dict[str, Any]:
    root = _normalize_root(project_root)
    detected = _detect_project_model(root)
    seeded = _base_project_config(root, detected)
    return validate_project_config(seeded, project_root=root)


def validate_project_config(
    config: dict[str, Any] | Any, *, project_root: str | Path | None = None
) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise ProjectConfigValidationError("Project config must be a JSON object")
    candidate = copy.deepcopy(config)
    _reject_secret_bearing_data(candidate)
    unknown = sorted(set(candidate) - set(TOP_LEVEL_SECTIONS))
    if unknown:
        raise ProjectConfigValidationError(
            f"Unknown top-level fields: {', '.join(unknown)}"
        )
    errors = sorted(_validator().iter_errors(candidate), key=_error_sort_key)
    if errors:
        raise ProjectConfigValidationError("; ".join(_format_error(err) for err in errors))
    normalized = _normalize_config(candidate)
    if project_root is not None:
        root = _normalize_root(project_root)
        expected_path = project_config_path(root)
        if not _is_within_root(expected_path, root):
            raise ProjectConfigValidationError("Project config path escapes the project root")
    return normalized


def load_project_config(project_root: str | Path) -> dict[str, Any]:
    root = _normalize_root(project_root)
    path = project_config_path(root)
    if not path.is_file():
        raise ProjectConfigNotFoundError(f"Project config was not found: {path}")
    return validate_project_config(_read_json_bounded(path), project_root=root)


def save_project_config(
    project_root: str | Path,
    config: dict[str, Any] | Any,
    *,
    expected_revision: int | None = None,
) -> dict[str, Any]:
    root = _normalize_root(project_root)
    path = project_config_path(root)
    validated = validate_project_config(config, project_root=root)
    current = load_project_config(root) if path.is_file() else None
    current_revision = None if current is None else int(current["revision"])
    requested_revision = validated["revision"] if expected_revision is None else expected_revision
    if current_revision is None:
        if requested_revision not in (None, 0):
            raise StaleProjectConfigError(
                f"Project config does not exist yet; expected revision 0, got {requested_revision}"
            )
        to_write = dict(validated)
        to_write["revision"] = 0
    else:
        if requested_revision != current_revision:
            raise StaleProjectConfigError(
                f"Stale project config revision: expected {current_revision}, got {requested_revision}"
            )
        to_write = dict(validated)
        to_write["revision"] = current_revision + 1
    to_write["provenance"] = dict(to_write["provenance"])
    to_write["provenance"]["updated"] = _utc_now()
    _atomic_write_json(path, to_write)
    return to_write


def refresh_project_config_diff(project_root: str | Path) -> dict[str, Any]:
    root = _normalize_root(project_root)
    path = project_config_path(root)
    current = load_project_config(root) if path.is_file() else None
    detected = _detect_project_model(root)
    if current is None:
        refreshed = validate_project_config(_base_project_config(root, detected), project_root=root)
    else:
        refreshed = _refresh_config(root, current, detected)
    changed_fields = _diff_paths(current, refreshed)
    return {
        "path": path.as_posix(),
        "exists": current is not None,
        "has_changes": bool(changed_fields),
        "changed_fields": changed_fields,
        "current": current,
        "refreshed": refreshed,
    }


def format_project_config(config: dict[str, Any] | Any) -> str:
    validated = validate_project_config(config)
    return json.dumps(validated, indent=2, ensure_ascii=False) + "\n"


def project_config_path(project_root: str | Path) -> Path:
    root = _normalize_root(project_root)
    config_path = (root / CONFIG_DIRNAME / CONFIG_FILENAME).resolve()
    if not _is_within_root(config_path, root):
        raise ProjectConfigError(f"Project config path escapes the project root: {config_path}")
    if config_path.exists() and config_path.is_symlink():
        raise ProjectConfigError(f"Refusing to use symlinked project config path: {config_path}")
    config_dir = config_path.parent
    if config_dir.exists() and config_dir.is_symlink():
        raise ProjectConfigError(f"Refusing to use symlinked config directory: {config_dir}")
    return config_path


def _normalize_root(project_root: str | Path) -> Path:
    root = Path(project_root).expanduser().resolve()
    if not root.exists():
        raise ProjectConfigError(f"Project root does not exist: {root}")
    if not root.is_dir():
        raise ProjectConfigError(f"Project root must be a directory: {root}")
    return root


def _validator() -> Draft202012Validator:
    if not hasattr(_validator, "_instance"):
        schema = _read_json_bounded(_resolve_schema_path())
        _validator._instance = Draft202012Validator(schema)
    return _validator._instance


def _resolve_schema_path() -> Path:
    package_dir = Path(__file__).resolve().parent
    candidates = (
        package_dir / "_runtime" / "schemas" / SCHEMA_FILENAME,
        package_dir.parents[1] / "schemas" / SCHEMA_FILENAME,
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise ProjectConfigError(
        "Unable to resolve project config schema from the source checkout or mission_directives/_runtime/schemas"
    )


def _read_json_bounded(path: Path, *, max_bytes: int = 16 * 1024 * 1024) -> Any:
    size = path.stat().st_size
    if size > max_bytes:
        raise ProjectConfigError(f"JSON file exceeds {max_bytes} bytes: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise ProjectConfigError(f"Refusing to write through a symlinked directory: {path.parent}")
    text = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def _error_sort_key(error: Any) -> tuple[Any, ...]:
    return tuple(str(part) for part in error.absolute_path)


def _format_error(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path) or "$"
    return f"{path}: {error.message}"


def _normalize_string_list(values: Any) -> list[str]:
    return [str(value).strip() for value in values]


def _normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(config)
    normalized["schema_version"] = str(normalized["schema_version"])
    normalized["revision"] = int(normalized["revision"])
    normalized["project"]["name"] = normalized["project"]["name"].strip()
    normalized["project"]["summary"] = normalized["project"]["summary"].strip()
    normalized["project"]["mission"] = normalized["project"]["mission"].strip()
    normalized["project"]["stage"] = normalized["project"]["stage"].strip()
    normalized["project"]["status"] = normalized["project"]["status"].strip()
    normalized["project"]["audiences"] = _normalize_string_list(normalized["project"]["audiences"])
    normalized["project"]["owners"] = _normalize_string_list(normalized["project"]["owners"])
    normalized["goals"]["outcomes"] = _normalize_string_list(normalized["goals"]["outcomes"])
    normalized["goals"]["success_criteria"] = _normalize_string_list(normalized["goals"]["success_criteria"])
    normalized["goals"]["non_goals"] = _normalize_string_list(normalized["goals"]["non_goals"])
    normalized["scope"]["include"] = _normalize_string_list(normalized["scope"]["include"])
    normalized["scope"]["exclude"] = _normalize_string_list(normalized["scope"]["exclude"])
    normalized["scope"]["protected_paths"] = _normalize_string_list(normalized["scope"]["protected_paths"])
    for section in ("stack", "paths", "commands", "constraints", "working_agreements", "current_state"):
        for key, value in normalized[section].items():
            normalized[section][key] = _normalize_string_list(value)
    normalized["provenance"]["updated"] = _normalize_optional_string(normalized["provenance"]["updated"])
    normalized["provenance"]["verified"] = _normalize_optional_string(normalized["provenance"]["verified"])
    normalized["provenance"]["source_paths"] = _normalize_string_list(normalized["provenance"]["source_paths"])
    return normalized


def _normalize_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).strip()


def _refresh_config(
    root: Path, current: dict[str, Any], detected: dict[str, Any]
) -> dict[str, Any]:
    refreshed = copy.deepcopy(current)
    derived = _base_project_config(root, detected)
    refreshed["project"]["name"] = derived["project"]["name"]
    if not refreshed["project"]["summary"].strip():
        refreshed["project"]["summary"] = derived["project"]["summary"]
    refreshed["stack"] = derived["stack"]
    refreshed["paths"] = derived["paths"]
    refreshed["commands"] = derived["commands"]
    refreshed["provenance"]["source_paths"] = derived["provenance"]["source_paths"]
    refreshed["extensions"] = _merge_extensions(current.get("extensions", {}), derived["extensions"])
    provisional = validate_project_config(refreshed, project_root=root)
    changes = _diff_paths(current, provisional)
    if changes:
        provisional["provenance"]["updated"] = _utc_now()
    else:
        provisional["provenance"]["updated"] = current["provenance"]["updated"]
    return validate_project_config(provisional, project_root=root)


def _merge_extensions(current: dict[str, Any], detected: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(current)
    merged["detection"] = detected["detection"]
    return merged


def _base_project_config(root: Path, detected: dict[str, Any]) -> dict[str, Any]:
    summary = detected["summary"] or f"Detected project context for {detected['name']}."
    return {
        "schema_version": SCHEMA_VERSION,
        "revision": 0,
        "project": {
            "name": detected["name"],
            "summary": summary,
            "mission": "",
            "stage": "discovered",
            "status": "active",
            "audiences": [],
            "owners": [],
        },
        "goals": {
            "outcomes": [],
            "success_criteria": [],
            "non_goals": [],
        },
        "scope": {
            "include": ["."],
            "exclude": [],
            "protected_paths": [f"{CONFIG_DIRNAME}/{CONFIG_FILENAME}"],
        },
        "stack": {
            "languages": detected["languages"],
            "frameworks": detected["frameworks"],
            "package_managers": detected["package_managers"],
            "services": detected["services"],
            "databases": detected["databases"],
            "deployment_targets": detected["deployment_targets"],
        },
        "paths": detected["paths"],
        "commands": detected["commands"],
        "constraints": {
            "security": [],
            "privacy": [],
            "legal": [],
            "compatibility": [],
            "performance": [],
            "budget": [],
        },
        "working_agreements": {
            "coding": [],
            "testing": [],
            "docs": [],
            "commit_messages": [],
        },
        "current_state": {
            "focus": [],
            "issues": [],
            "decisions": [],
            "questions": [],
        },
        "provenance": {
            "updated": _utc_now(),
            "verified": None,
            "source_paths": detected["source_paths"],
        },
        "extensions": {
            "detection": {
                "manifests": detected["manifests"],
                "ecosystems": detected["ecosystems"],
                "package_managers": detected["package_managers"],
            }
        },
    }


def _detect_project_model(root: Path) -> dict[str, Any]:
    manifests: list[dict[str, Any]] = []
    for directory in _candidate_directories(root):
        for filename, detector in _MANIFEST_DETECTORS:
            candidate = directory / filename
            if not candidate.is_file():
                continue
            manifest = detector(root, candidate)
            if manifest is not None:
                manifests.append(manifest)
    manifests.sort(key=lambda item: item["path"])
    ecosystems = sorted({item["ecosystem"] for item in manifests})
    package_managers = sorted(
        {item["package_manager"] for item in manifests if item["package_manager"]}
    )
    if not package_managers and any(item["kind"] == "package.json" for item in manifests):
        package_managers = ["npm"]
    dependencies = sorted(
        {
            dependency
            for manifest in manifests
            for dependency in manifest.get("dependencies", [])
        }
    )
    return {
        "name": _detect_project_name(root, manifests),
        "summary": _detect_project_summary(manifests),
        "manifests": manifests,
        "ecosystems": ecosystems,
        "languages": sorted(
            {LANGUAGE_BY_ECOSYSTEM[item] for item in ecosystems if item in LANGUAGE_BY_ECOSYSTEM}
        ),
        "frameworks": _detect_named_hints(dependencies, FRAMEWORK_HINTS),
        "package_managers": package_managers,
        "services": _detect_named_hints(dependencies, SERVICE_HINTS),
        "databases": _detect_named_hints(dependencies, DATABASE_HINTS),
        "deployment_targets": _detect_named_hints(dependencies, DEPLOYMENT_HINTS),
        "paths": _detect_paths(root),
        "commands": _detect_commands(root, manifests, package_managers, dependencies),
        "source_paths": sorted({item["path"] for item in manifests}),
    }


def _candidate_directories(root: Path) -> list[Path]:
    directories = [root]
    child_dirs = sorted(
        [child for child in root.iterdir() if child.is_dir() and not child.name.startswith(".")],
        key=lambda item: item.name.lower(),
    )
    directories.extend(child_dirs[:MAX_DETECTION_DIRS])
    return directories


def _detect_project_name(root: Path, manifests: list[dict[str, Any]]) -> str:
    for manifest in manifests:
        if manifest["directory"] == "." and manifest.get("name"):
            return manifest["name"]
    for manifest in manifests:
        if manifest.get("name"):
            return manifest["name"]
    return root.name


def _detect_project_summary(manifests: list[dict[str, Any]]) -> str:
    for manifest in manifests:
        summary = manifest.get("summary")
        if isinstance(summary, str) and summary.strip():
            return summary.strip()
    return ""


def _detect_named_hints(dependencies: list[str], mapping: dict[str, str]) -> list[str]:
    found = set()
    lowered = {dependency.lower() for dependency in dependencies}
    for dependency in lowered:
        for fragment, label in mapping.items():
            if fragment in dependency:
                found.add(label)
    return sorted(found)


def _detect_paths(root: Path) -> dict[str, list[str]]:
    def existing_paths(candidates: list[str]) -> list[str]:
        paths: list[str] = []
        for candidate in candidates:
            path = root / candidate
            if path.exists():
                paths.append(path.relative_to(root).as_posix())
        return paths

    entrypoints = existing_paths(
        [
            "main.py",
            "app.py",
            "manage.py",
            "server.py",
            "wsgi.py",
            "asgi.py",
            "src/main.rs",
            "src/lib.rs",
            "cmd/main.go",
            "src/main.go",
        ]
    )
    return {
        "source": existing_paths(["src", "app", "lib", "cmd"]),
        "tests": existing_paths(["tests", "test", "spec"]),
        "docs": existing_paths(["docs", "doc"]),
        "entrypoints": entrypoints,
        "generated_outputs": existing_paths(["dist", "build", "target", "coverage", "site/dist"]),
    }


def _detect_commands(
    root: Path,
    manifests: list[dict[str, Any]],
    package_managers: list[str],
    dependencies: list[str],
) -> dict[str, list[str]]:
    commands = {
        "setup": [],
        "development": [],
        "test": [],
        "lint": [],
        "typecheck": [],
        "build": [],
        "package": [],
    }
    for manifest in manifests:
        if manifest["kind"] == "package.json":
            manager = manifest.get("package_manager") or "npm"
            scripts = manifest.get("scripts", {})
            for command_type, script_names in {
                "development": ("dev", "start"),
                "test": ("test",),
                "lint": ("lint",),
                "typecheck": ("typecheck", "check-types"),
                "build": ("build",),
                "package": ("package", "pack"),
            }.items():
                for script_name in script_names:
                    if script_name in scripts:
                        commands[command_type].append(f"{manager} run {script_name}")
                        break
            install = {
                "pnpm": "pnpm install",
                "yarn": "yarn install",
            }.get(manager, f"{manager} install")
            commands["setup"].append(install)
        elif manifest["kind"] == "Cargo.toml":
            commands["development"].append("cargo run")
            commands["test"].append("cargo test")
            commands["lint"].append("cargo clippy --all-targets --all-features")
            commands["typecheck"].append("cargo check")
            commands["build"].append("cargo build")
            commands["package"].append("cargo package")
        elif manifest["kind"] == "go.mod":
            commands["development"].append("go run ./...")
            commands["test"].append("go test ./...")
            commands["build"].append("go build ./...")
        elif manifest["kind"] == "pom.xml":
            commands["test"].append("mvn test")
            commands["build"].append("mvn package")
            commands["package"].append("mvn package")
        elif manifest["kind"] in {"build.gradle", "build.gradle.kts"}:
            commands["test"].append("./gradlew test")
            commands["build"].append("./gradlew build")
        elif manifest["kind"] in {"pyproject.toml", "requirements.txt", "requirements-dev.txt", "requirements-runtime.txt", "setup.py", "setup.cfg"}:
            if (root / "requirements-dev.txt").is_file():
                commands["setup"].append("python -m pip install -r requirements-dev.txt")
            elif (root / "requirements.txt").is_file():
                commands["setup"].append("python -m pip install -r requirements.txt")
            elif (root / "pyproject.toml").is_file():
                commands["setup"].append("python -m pip install -e .")
            if (root / "tests").exists():
                commands["test"].append("python -m pytest")
            if any(dep.lower().startswith("ruff") for dep in dependencies):
                commands["lint"].append("python -m ruff check .")
            if any(dep.lower().startswith("mypy") for dep in dependencies):
                commands["typecheck"].append("python -m mypy .")
            if any(dep.lower().startswith("pyright") for dep in dependencies):
                commands["typecheck"].append("pyright")
            if (root / "pyproject.toml").is_file():
                commands["build"].append("python -m build")
                commands["package"].append("python -m build")
    return {key: _dedupe_preserve_order(value) for key, value in commands.items()}


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _relative_directory(root: Path, path: Path) -> str:
    directory = path.parent.relative_to(root).as_posix()
    return directory or "."


def _manifest_entry(
    root: Path,
    path: Path,
    *,
    kind: str,
    ecosystem: str,
    package_manager: str | None,
    name: str | None = None,
    summary: str | None = None,
    scripts: dict[str, str] | None = None,
    dependencies: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "kind": kind,
        "path": path.relative_to(root).as_posix(),
        "directory": _relative_directory(root, path),
        "name": name,
        "summary": summary,
        "ecosystem": ecosystem,
        "package_manager": package_manager,
        "scripts": scripts or {},
        "dependencies": sorted(dependencies or []),
    }


def _read_text_bounded(path: Path, *, max_bytes: int = MAX_MANIFEST_BYTES) -> str:
    size = path.stat().st_size
    if size > max_bytes:
        raise ProjectConfigError(f"Manifest exceeds {max_bytes} bytes: {path}")
    return path.read_text(encoding="utf-8")


def _read_toml_bounded(path: Path) -> dict[str, Any]:
    size = path.stat().st_size
    if size > MAX_MANIFEST_BYTES:
        raise ProjectConfigError(f"Manifest exceeds {MAX_MANIFEST_BYTES} bytes: {path}")
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _detect_package_json(root: Path, path: Path) -> dict[str, Any]:
    payload = _read_json_bounded(path, max_bytes=MAX_MANIFEST_BYTES)
    package_manager = payload.get("packageManager")
    manager = None
    if isinstance(package_manager, str) and package_manager.strip():
        manager = package_manager.split("@", 1)[0].strip() or None
    dependencies = _dict_keys(payload.get("dependencies")) + _dict_keys(payload.get("devDependencies"))
    scripts = payload.get("scripts") if isinstance(payload.get("scripts"), dict) else {}
    name = payload.get("name")
    summary = payload.get("description")
    return _manifest_entry(
        root,
        path,
        kind="package.json",
        ecosystem="node",
        package_manager=manager,
        name=name if isinstance(name, str) and name.strip() else None,
        summary=summary if isinstance(summary, str) and summary.strip() else None,
        scripts={str(key): str(value) for key, value in scripts.items()},
        dependencies=dependencies,
    )


def _detect_pyproject(root: Path, path: Path) -> dict[str, Any]:
    payload = _read_toml_bounded(path)
    project = payload.get("project") if isinstance(payload.get("project"), dict) else {}
    tool = payload.get("tool") if isinstance(payload.get("tool"), dict) else {}
    poetry = tool.get("poetry") if isinstance(tool.get("poetry"), dict) else {}
    name = project.get("name") or poetry.get("name")
    summary = project.get("description") or poetry.get("description")
    dependencies = []
    dependencies.extend(_iter_dependency_names(project.get("dependencies")))
    optional = project.get("optional-dependencies")
    if isinstance(optional, dict):
        for value in optional.values():
            dependencies.extend(_iter_dependency_names(value))
    dependencies.extend(_dict_keys(poetry.get("dependencies")))
    dependencies.extend(_dict_keys(poetry.get("group", {})))
    return _manifest_entry(
        root,
        path,
        kind="pyproject.toml",
        ecosystem="python",
        package_manager="pip",
        name=name if isinstance(name, str) and name.strip() else None,
        summary=summary if isinstance(summary, str) and summary.strip() else None,
        dependencies=dependencies,
    )


def _detect_requirements(root: Path, path: Path) -> dict[str, Any]:
    text = _read_text_bounded(path)
    return _manifest_entry(
        root,
        path,
        kind=path.name,
        ecosystem="python",
        package_manager="pip",
        dependencies=_requirements_dependencies(text),
    )


def _detect_setup(root: Path, path: Path) -> dict[str, Any]:
    _read_text_bounded(path)
    return _manifest_entry(
        root,
        path,
        kind=path.name,
        ecosystem="python",
        package_manager="pip",
    )


def _detect_cargo(root: Path, path: Path) -> dict[str, Any]:
    payload = _read_toml_bounded(path)
    package = payload.get("package") if isinstance(payload.get("package"), dict) else {}
    dependencies = _dict_keys(payload.get("dependencies")) + _dict_keys(payload.get("dev-dependencies"))
    return _manifest_entry(
        root,
        path,
        kind="Cargo.toml",
        ecosystem="rust",
        package_manager="cargo",
        name=package.get("name") if isinstance(package.get("name"), str) else None,
        summary=package.get("description") if isinstance(package.get("description"), str) else None,
        dependencies=dependencies,
    )


def _detect_go(root: Path, path: Path) -> dict[str, Any]:
    text = _read_text_bounded(path)
    name = None
    dependencies: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("module "):
            name = stripped.removeprefix("module ").strip() or None
        elif stripped.startswith("require "):
            parts = stripped.split()
            if len(parts) >= 2:
                dependencies.append(parts[1])
    return _manifest_entry(
        root,
        path,
        kind="go.mod",
        ecosystem="go",
        package_manager="go",
        name=name,
        dependencies=dependencies,
    )


def _detect_pom(root: Path, path: Path) -> dict[str, Any]:
    parsed = ET.fromstring(_read_text_bounded(path))
    dependencies = []
    for element in parsed.iter():
        if element.tag.rsplit("}", 1)[-1] == "artifactId":
            text = (element.text or "").strip()
            if text:
                dependencies.append(text)
    return _manifest_entry(
        root,
        path,
        kind="pom.xml",
        ecosystem="java",
        package_manager="maven",
        name=_xml_text(parsed, "artifactId") or _xml_text(parsed, "name"),
        summary=_xml_text(parsed, "description"),
        dependencies=dependencies,
    )


def _detect_gradle(root: Path, path: Path) -> dict[str, Any]:
    text = _read_text_bounded(path)
    match = re.search(r"rootProject\.name\s*=\s*['\"]([^'\"]+)['\"]", text)
    dependencies = re.findall(r"['\"]([A-Za-z0-9_.-]+(?::[A-Za-z0-9_.-]+)+)['\"]", text)
    return _manifest_entry(
        root,
        path,
        kind=path.name,
        ecosystem="java",
        package_manager="gradle",
        name=match.group(1).strip() if match else None,
        dependencies=dependencies,
    )


def _detect_gemfile(root: Path, path: Path) -> dict[str, Any]:
    text = _read_text_bounded(path)
    dependencies = re.findall(r"^\s*gem\s+['\"]([^'\"]+)['\"]", text, flags=re.MULTILINE)
    return _manifest_entry(
        root,
        path,
        kind="Gemfile",
        ecosystem="ruby",
        package_manager="bundler",
        dependencies=dependencies,
    )


def _detect_composer(root: Path, path: Path) -> dict[str, Any]:
    payload = _read_json_bounded(path, max_bytes=MAX_MANIFEST_BYTES)
    dependencies = _dict_keys(payload.get("require")) + _dict_keys(payload.get("require-dev"))
    name = payload.get("name")
    summary = payload.get("description")
    return _manifest_entry(
        root,
        path,
        kind="composer.json",
        ecosystem="php",
        package_manager="composer",
        name=name if isinstance(name, str) and name.strip() else None,
        summary=summary if isinstance(summary, str) and summary.strip() else None,
        dependencies=dependencies,
    )


def _xml_text(root: ET.Element, tag: str) -> str | None:
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] == tag:
            text = (element.text or "").strip()
            if text:
                return text
    return None


def _dict_keys(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return []
    return [str(key) for key in value.keys()]


def _iter_dependency_names(value: Any) -> list[str]:
    if isinstance(value, list):
        results: list[str] = []
        for item in value:
            if isinstance(item, str):
                name = re.split(r"[<>=!~ \[]", item, maxsplit=1)[0].strip()
                if name:
                    results.append(name)
        return results
    if isinstance(value, dict):
        return _dict_keys(value)
    return []


def _requirements_dependencies(text: str) -> list[str]:
    results: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-"):
            continue
        name = re.split(r"[<>=!~ \[]", stripped, maxsplit=1)[0].strip()
        if name:
            results.append(name)
    return results


def _reject_secret_bearing_data(value: Any, *, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if SENSITIVE_KEY_RE.search(key_text):
                raise ProjectConfigSecretError(f"Secret-bearing key is not allowed at {child_path}")
            _reject_secret_bearing_data(item, path=child_path)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _reject_secret_bearing_data(item, path=f"{path}[{index}]")
        return
    if isinstance(value, str):
        for pattern in SENSITIVE_VALUE_PATTERNS:
            if pattern.search(value):
                raise ProjectConfigSecretError(f"Secret-bearing value is not allowed at {path}")


def _diff_paths(before: Any, after: Any, *, path: str = "$") -> list[str]:
    if before == after:
        return []
    if before is None or after is None:
        return [path]
    if isinstance(before, dict) and isinstance(after, dict):
        changes: list[str] = []
        for key in sorted(set(before) | set(after)):
            child_path = key if path == "$" else f"{path}.{key}"
            if key not in before or key not in after:
                changes.append(child_path)
                continue
            changes.extend(_diff_paths(before[key], after[key], path=child_path))
        return changes
    if isinstance(before, list) and isinstance(after, list):
        max_len = max(len(before), len(after))
        changes: list[str] = []
        for index in range(max_len):
            child_path = f"{path}[{index}]"
            if index >= len(before) or index >= len(after):
                changes.append(child_path)
                continue
            changes.extend(_diff_paths(before[index], after[index], path=child_path))
        return changes
    return [path]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _is_within_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


_MANIFEST_DETECTORS: tuple[tuple[str, Callable[[Path, Path], dict[str, Any] | None]], ...] = (
    ("pyproject.toml", _detect_pyproject),
    ("requirements.txt", _detect_requirements),
    ("requirements-dev.txt", _detect_requirements),
    ("requirements-runtime.txt", _detect_requirements),
    ("setup.py", _detect_setup),
    ("setup.cfg", _detect_setup),
    ("package.json", _detect_package_json),
    ("Cargo.toml", _detect_cargo),
    ("go.mod", _detect_go),
    ("pom.xml", _detect_pom),
    ("build.gradle", _detect_gradle),
    ("build.gradle.kts", _detect_gradle),
    ("Gemfile", _detect_gemfile),
    ("composer.json", _detect_composer),
)
