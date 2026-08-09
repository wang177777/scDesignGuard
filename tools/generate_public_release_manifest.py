#!/usr/bin/env python3
"""Generate deterministic public-release manifest and SHA-256 sidecar list."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKSUMS = ROOT / "PUBLIC_RELEASE_CHECKSUMS.sha256"
MANIFEST = ROOT / "PUBLIC_RELEASE_MANIFEST.csv"
EXCLUDED = {CHECKSUMS, MANIFEST}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def category(relative: str) -> tuple[str, str]:
    if relative.startswith("paper/"):
        return "PROJECT_GENERATED_PUBLICATION_ARTIFACT", "CC-BY-4.0"
    if relative.startswith("artifacts/"):
        return "EVALUATED_SOFTWARE_ARTIFACT", "BSD-3-Clause"
    if relative.startswith("src/") or relative.startswith("tests/") or relative.startswith("analysis_scripts/") or relative.startswith("tools/"):
        return "SOURCE_OR_TEST_CODE", "BSD-3-Clause"
    return "PUBLIC_DOCUMENTATION_OR_METADATA", "BSD-3-Clause"


def main() -> None:
    files = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file() and path not in EXCLUDED and ".git" not in path.parts and "__pycache__" not in path.parts
    )
    rows = []
    checksums = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        sha = digest(path)
        kind, license_id = category(relative)
        rows.append((relative, path.stat().st_size, sha, kind, license_id))
        checksums.append(f"{sha}  {relative}")
    with MANIFEST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["path", "bytes", "sha256", "artifact_class", "license"])
        writer.writerows(rows)
    checksums.append(f"{digest(MANIFEST)}  {MANIFEST.relative_to(ROOT).as_posix()}")
    CHECKSUMS.write_text("\n".join(checksums) + "\n", encoding="utf-8")
    print(f"manifested {len(files)} files")


if __name__ == "__main__":
    main()
