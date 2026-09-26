from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from rejuv.models import CURRENT_SCHEMA_VERSION, intervention_episode_json_schema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_RELATIVE = Path("schemas/intervention_episode.schema.json")
SCHEMA_PATH = ROOT / SCHEMA_RELATIVE
SEMVER_RE = re.compile(r"^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)$")


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_semver(value: str) -> tuple[int, int, int]:
    match = SEMVER_RE.fullmatch(value)
    if match is None:
        raise ValueError(f"Invalid semantic version: {value!r}")
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def schema_version(schema: dict[str, Any]) -> str:
    value = schema.get("x-rejuv-schema-version")
    if isinstance(value, str):
        return value

    property_schema = schema.get("properties", {}).get("schema_version", {})
    const = property_schema.get("const")
    if isinstance(const, str):
        return const

    raise ValueError("JSON Schema does not expose a Rejuv schema version.")


def load_base_schema() -> dict[str, Any] | None:
    """Load the base-branch schema during a GitHub pull request, if one exists."""
    base_ref = os.environ.get("GITHUB_BASE_REF")
    if not base_ref:
        return None

    for git_ref in (f"origin/{base_ref}", base_ref):
        result = subprocess.run(
            ["git", "show", f"{git_ref}:{SCHEMA_RELATIVE.as_posix()}"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)

    # The first PR that introduces the generated artifact has no base schema.
    return None


def main() -> int:
    if not SCHEMA_PATH.exists():
        print(
            f"Missing generated schema: {SCHEMA_RELATIVE}. "
            "Run `python scripts/export_schema.py` and commit the result.",
            file=sys.stderr,
        )
        return 1

    checked_in = load_json(SCHEMA_PATH)
    generated = intervention_episode_json_schema()

    if canonical_json(checked_in) != canonical_json(generated):
        print(
            "Generated JSON Schema differs from the checked-in artifact. "
            "Run `python scripts/export_schema.py`, review the diff, and commit it.",
            file=sys.stderr,
        )
        return 1

    current_version = schema_version(checked_in)
    if current_version != CURRENT_SCHEMA_VERSION:
        print(
            "Schema metadata and CURRENT_SCHEMA_VERSION disagree: "
            f"{current_version!r} != {CURRENT_SCHEMA_VERSION!r}.",
            file=sys.stderr,
        )
        return 1

    try:
        parse_semver(current_version)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    base_schema = load_base_schema()
    if base_schema is not None and canonical_json(base_schema) != canonical_json(checked_in):
        base_version = schema_version(base_schema)

        try:
            old = parse_semver(base_version)
            new = parse_semver(current_version)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        if new <= old:
            print(
                "The generated schema changed but schema_version was not increased: "
                f"{base_version} -> {current_version}. "
                "Bump the schema version according to RFC-0001 and document compatibility.",
                file=sys.stderr,
            )
            return 1

    print(f"Schema contract OK: {current_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
