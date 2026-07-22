#!/usr/bin/env python3
"""Shared filesystem, identifier, and atomic-I/O security primitives.

These helpers deliberately fail closed.  They are used by installers and tools
that accept user-controlled identifiers or paths, and therefore must not follow
symbolic links or allow writes outside their declared roots.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
from pathlib import Path
from typing import Any, Iterable

_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,126}[A-Za-z0-9])?$")


def validate_identifier(value: str, *, kind: str = "identifier") -> str:
    """Validate a single path-component identifier.

    Dots are allowed for semantic versions, but consecutive dots and leading or
    trailing punctuation are rejected to prevent traversal and ambiguous names.
    """
    if not isinstance(value, str) or value != value.strip() or not value:
        raise ValueError(f"Invalid {kind} identifier")
    if value in {".", ".."} or ".." in value:
        raise ValueError(f"Invalid {kind} identifier: traversal is not allowed")
    if any(ch in value for ch in ("/", "\\", ":", "\x00")):
        raise ValueError(f"Invalid {kind} identifier: path syntax is not allowed")
    if not _IDENTIFIER_RE.fullmatch(value):
        raise ValueError(
            f"Invalid {kind} identifier: use 1-128 letters, digits, dots, underscores, or hyphens; "
            "begin and end with a letter or digit"
        )
    return value


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(os.path.expanduser(str(path))))


def ensure_no_symlink_components(path: Path, *, include_leaf: bool = True) -> Path:
    """Reject symbolic-link components that could be user-controlled.

    Allows known-safe system symlinks (e.g., ``/var -> /private/var`` on macOS)
    where the symlink's parent directory is not writable by the current user.
    """
    absolute = _absolute_lexical(path)
    parts = absolute.parts
    if not parts:
        return absolute
    current = Path(parts[0])
    end = len(parts) if include_leaf else max(1, len(parts) - 1)
    for idx, part in enumerate(parts[1:end], start=1):
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            _check_symlink(current)
            resolved = current.resolve(strict=False)
            if resolved == current:
                raise ValueError(f"Refusing unresolvable symlink: {current}")
            remaining = Path(*parts[idx + 1 :])
            return ensure_no_symlink_components(
                resolved / remaining, include_leaf=include_leaf
            )
    return absolute


def _check_symlink(path: Path) -> None:
    """Reject a symlink in a user-writable directory; allow system symlinks."""
    try:
        parent_st = path.parent.lstat()
    except OSError:
        raise ValueError(f"Refusing symlink: {path}")
    if os.name == "nt":
        raise ValueError(f"Refusing symlink component: {path}")
    # Symlinks in root-owned, non-world-writable directories are safe system symlinks
    if parent_st.st_uid != 0 or (parent_st.st_mode & 0o2):
        raise ValueError(f"Refusing symlink component: {path}")


def is_within(path: Path, root: Path) -> bool:
    p = _absolute_lexical(path)
    r = _absolute_lexical(root)
    try:
        p.relative_to(r)
        return True
    except ValueError:
        return False


def safe_child(base: Path, child: str | Path, *, reject_symlinks: bool = True) -> Path:
    """Return a child path only when it remains lexically contained in *base*."""
    base_abs = _absolute_lexical(base)
    raw = Path(child)
    if raw.is_absolute() or any(part in {"", ".", ".."} for part in raw.parts):
        raise ValueError(f"Unsafe child path: {child}")
    candidate = _absolute_lexical(base_abs / raw)
    if candidate == base_abs or not is_within(candidate, base_abs):
        raise ValueError(f"Path escapes declared root: {child}")
    if reject_symlinks:
        ensure_no_symlink_components(base_abs)
        ensure_no_symlink_components(candidate)
    return candidate


def validate_distinct_roots(roots: Iterable[Path]) -> list[Path]:
    """Require non-overlapping roots before a multi-destination mutation."""
    normalized = [_absolute_lexical(p) for p in roots]
    if len({os.path.normcase(str(p)) for p in normalized}) != len(normalized):
        raise ValueError("Destination roots must be distinct")
    for index, left in enumerate(normalized):
        ensure_no_symlink_components(left)
        for right in normalized[index + 1 :]:
            if is_within(left, right) or is_within(right, left):
                raise ValueError(f"Destination roots overlap: {left} and {right}")
    return normalized


def _fsync_directory(directory: Path) -> None:
    if os.name == "nt":
        return
    try:
        fd = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write_bytes(path: Path, data: bytes, *, default_mode: int = 0o644) -> None:
    path = _absolute_lexical(path)
    ensure_no_symlink_components(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ensure_no_symlink_components(path.parent)
    mode = default_mode
    if path.exists():
        if path.is_symlink():
            raise ValueError(f"Refusing to replace symlink: {path}")
        mode = stat.S_IMODE(path.stat().st_mode)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(tmp_name)
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(fd, mode)
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        try:
            os.chmod(path, mode)
        except OSError:
            pass
        _fsync_directory(path.parent)
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        temporary.unlink(missing_ok=True)
        raise


def atomic_write_text(path: Path, text: str, *, default_mode: int = 0o644) -> None:
    atomic_write_bytes(path, text.encode("utf-8"), default_mode=default_mode)


def atomic_write_json(path: Path, value: Any, *, default_mode: int = 0o644) -> None:
    atomic_write_text(
        path,
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        default_mode=default_mode,
    )


def _win_long_path(path: Path) -> str | Path:
    if os.name != "nt":
        return path
    absolute = os.path.abspath(str(path))
    if absolute.startswith("\\\\?\\"):
        return absolute
    if absolute.startswith("\\\\"):
        return "\\\\?\\UNC\\" + absolute[2:]
    return "\\\\?\\" + absolute


def _win_normal_path(path: str) -> Path:
    if path.startswith("\\\\?\\UNC\\"):
        return Path("\\\\" + path[8:])
    if path.startswith("\\\\?\\"):
        return Path(path[4:])
    return Path(path)


def iter_tree_files(root: Path) -> Iterable[Path]:
    root = _absolute_lexical(root)
    ensure_no_symlink_components(root)
    if not root.is_dir():
        raise ValueError(f"Expected directory: {root}")
    for directory, dirnames, filenames in os.walk(
        _win_long_path(root), topdown=True, followlinks=False
    ):
        current = _win_normal_path(str(directory))
        check_current = Path(directory)
        for name in list(dirnames):
            if name == ".venv":
                dirnames.remove(name)
                continue
            candidate = check_current / name
            if candidate.is_symlink():
                raise ValueError(
                    f"Symlinks are not allowed in source trees: {current / name}"
                )
        for name in filenames:
            candidate = check_current / name
            if candidate.is_symlink():
                raise ValueError(
                    f"Symlinks are not allowed in source trees: {current / name}"
                )
            if not candidate.is_file():
                raise ValueError(f"Unsupported non-regular file: {current / name}")
            yield current / name


def validate_tree_limits(
    root: Path,
    *,
    max_files: int = 20_000,
    max_total_bytes: int = 512 * 1024 * 1024,
    max_file_bytes: int = 128 * 1024 * 1024,
) -> dict[str, int]:
    """Reject pathological trees before copying or hashing them."""
    count = 0
    total = 0
    for path in iter_tree_files(root):
        size = path.stat().st_size
        count += 1
        total += size
        if count > max_files:
            raise ValueError(f"Tree exceeds {max_files} regular files")
        if size > max_file_bytes:
            raise ValueError(f"File exceeds {max_file_bytes} bytes: {path}")
        if total > max_total_bytes:
            raise ValueError(f"Tree exceeds {max_total_bytes} total bytes")
    return {"files": count, "bytes": total}


def tree_digest(root: Path) -> str:
    """Hash names, sizes, and bytes for an entire regular-file tree without loading large files into memory."""
    root = _absolute_lexical(root)
    digest = hashlib.sha256()
    for path in sorted(
        iter_tree_files(root), key=lambda p: p.relative_to(root).as_posix()
    ):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        size = path.stat().st_size
        digest.update(len(rel).to_bytes(8, "big"))
        digest.update(rel)
        digest.update(size.to_bytes(8, "big"))
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
    return digest.hexdigest()


def read_json_bounded(path: Path, *, max_bytes: int = 16 * 1024 * 1024) -> Any:
    """Read a regular UTF-8 JSON file with a strict size bound."""
    path = ensure_no_symlink_components(path)
    if not path.is_file():
        raise ValueError(f"Expected regular JSON file: {path}")
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"JSON file exceeds {max_bytes} bytes: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


from contextlib import contextmanager


@contextmanager
def exclusive_lock(lock_path: Path):
    """Cross-platform advisory lock stored next to the protected artifact."""
    lock_path = _absolute_lexical(lock_path)
    ensure_no_symlink_components(lock_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(lock_path, flags, 0o600)
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
            raise ValueError(
                f"Lock path must be a single-link regular file: {lock_path}"
            )
        try:
            os.chmod(lock_path, 0o600)
        except OSError:
            pass
        if os.name == "nt":
            import msvcrt

            os.lseek(fd, 0, os.SEEK_SET)
            os.write(fd, b"0")
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


_GITHUB_REPO_RE = re.compile(r"^/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?$")
_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def validate_sha1(value: str, *, kind: str = "commit SHA") -> str:
    if not isinstance(value, str) or not _SHA1_RE.fullmatch(value.lower()):
        raise ValueError(
            f"Invalid {kind}; expected 40 lowercase hexadecimal characters"
        )
    return value.lower()


def validate_sha256(value: str, *, kind: str = "SHA-256") -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value.lower()):
        raise ValueError(
            f"Invalid {kind}; expected 64 lowercase hexadecimal characters"
        )
    return value.lower()


def validate_github_repository(value: str) -> str:
    """Accept one canonical HTTPS GitHub owner/repository URL only."""
    from urllib.parse import urlsplit, urlunsplit

    if not isinstance(value, str) or value != value.strip():
        raise ValueError("Invalid repository URL")
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "github.com"
        or parsed.port is not None
    ):
        raise ValueError("Repository must use canonical HTTPS github.com transport")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(
            "Repository URL must not contain credentials, query parameters, or fragments"
        )
    parts = parsed.path.strip("/").split("/")
    if len(parts) != 2:
        raise ValueError("Repository must identify exactly one GitHub owner/repository")
    owner, repository = parts
    if repository.endswith(".git"):
        repository = repository[:-4]
    for label, component in (("owner", owner), ("repository", repository)):
        if not component or component in {".", ".."} or ".." in component:
            raise ValueError(f"Invalid GitHub {label}")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", component):
            raise ValueError(f"Invalid GitHub {label}")
    return urlunsplit(("https", "github.com", f"/{owner}/{repository}", "", ""))


def bounded_response_bytes(
    response: Any, *, max_bytes: int = 64 * 1024 * 1024
) -> bytes:
    """Read an HTTP response without trusting Content-Length."""
    declared = response.headers.get("Content-Length")
    if declared:
        try:
            declared_size = int(declared)
        except (TypeError, ValueError):
            declared_size = -1
        if declared_size > max_bytes:
            raise ValueError(f"Response exceeds {max_bytes} byte limit")
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = response.read(min(1024 * 1024, max_bytes + 1 - total))
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ValueError(f"Response exceeds {max_bytes} byte limit")
        chunks.append(chunk)
    return b"".join(chunks)


def github_tarball_sha256(repository: str, commit: str, *, timeout: int = 60) -> str:
    """Download one pinned GitHub tarball and return its bounded SHA-256 digest."""
    import urllib.request
    from urllib.parse import urlsplit

    repository = validate_github_repository(repository)
    commit = validate_sha1(commit)
    owner_repo = urlsplit(repository).path.strip("/")
    url = f"https://github.com/{owner_repo}/archive/{commit}.tar.gz"
    request = urllib.request.Request(
        url, headers={"User-Agent": "mission-directives/1"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        final = urlsplit(response.geturl())
        if final.scheme != "https" or final.hostname not in {
            "github.com",
            "codeload.github.com",
        }:
            raise ValueError("Tarball redirect left approved GitHub hosts")
        return hashlib.sha256(bounded_response_bytes(response)).hexdigest()


def remove_tree(path: Path) -> None:
    """Remove a normal directory tree without following a symlink leaf."""
    import shutil

    path = _absolute_lexical(path)
    ensure_no_symlink_components(path)
    if not path.exists():
        return
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"Refusing to remove non-directory or symlink path: {path}")
    shutil.rmtree(_win_long_path(path))
