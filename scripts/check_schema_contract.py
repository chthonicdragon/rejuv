from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from rejuv.models import CURRENT_SCHEMA_VERSION, intervention_episode_json_schema
from rejuv.releases import DataReleaseManifest, RELEASE_MANIFEST_VERSION
from rejuv.sources import SOURCE_CONTRACT_VERSION, SourceManifest
from rejuv.validation import (
    VALIDATION_PROFILE_VERSION,
    strict_data_release_manifest_schema,
    strict_intervention_episode_schema,
    strict_source_manifest_schema,
    validation_profile,
)


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = "v" + VALIDATION_PROFILE_VERSION.replace(".", "_")
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")

GENERATED_ARTIFACTS: dict[Path, dict[str, Any]] = {
    Path("schemas/intervention_episode.schema.json"): intervention_episode_json_schema(),
    Path("schemas/source_manifest.schema.json"): SourceManifest.model_json_schema(),
    Path("schemas/data_release_manifest.schema.json"): DataReleaseManifest.model_json_schema(),
    Path(f"schemas/validation/{PROFILE_DIR}/intervention_episode.schema.json"): (
        strict_intervention_episode_schema()
    ),
    Path(f"schemas/validation/{PROFILE_DIR}/source_manifest.schema.json"): (
        strict_source_manifest_schema()
    ),
    Path(f"schemas/validation/{PROFILE_DIR}/data_release_manifest.schema.json"): (
        strict_data_release_manifest_schema()
    ),
    Path(f"schemas/validation/{PROFILE_DIR}/profile.json"): validation_profile(),
}


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


def contract_version(schema: dict[str, Any], metadata_key: str) -> str:
    value = schema.get(metadata_key)
    if isinstance(value, str):
        return value
    raise ValueError(f"JSON Schema does not expose contract metadata {metadata_key!r}.")


def load_base_schema(relative_path: Path) -> dict[str, Any] | None:
    base_ref = os.environ.get("GITHUB_BASE_REF")
    if not base_ref:
        return None

    for git_ref in (f"origin/{base_ref}", base_ref):
        result = subprocess.run(
            ["git", "show", f"{git_ref}:{relative_path.as_posix()}"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    return None


def check_generated_artifacts() -> list[str]:
    errors: list[str] = []
    for relative_path, generated in GENERATED_ARTIFACTS.items():
        path = ROOT / relative_path
        if not path.exists():
            errors.append(
                f"Missing generated artifact: {relative_path}. "
                "Run `python scripts/export_schema.py`."
            )
            continue
        checked_in = load_json(path)
        if canonical_json(checked_in) != canonical_json(generated):
            errors.append(
                f"Generated artifact differs from checked-in file: {relative_path}. "
                "Run `python scripts/export_schema.py`."
            )
    return errors


def check_public_schema_versions() -> list[str]:
    contracts = (
        (
            Path("schemas/intervention_episode.schema.json"),
            "x-rejuv-schema-version",
            CURRENT_SCHEMA_VERSION,
        ),
        (
            Path("schemas/source_manifest.schema.json"),
            "x-rejuv-source-contract-version",
            SOURCE_CONTRACT_VERSION,
        ),
        (
            Path("schemas/data_release_manifest.schema.json"),
            "x-rejuv-release-manifest-version",
            RELEASE_MANIFEST_VERSION,
        ),
    )
    errors: list[str] = []

    for relative_path, metadata_key, expected_version in contracts:
        checked_in = load_json(ROOT / relative_path)
        current_version = contract_version(checked_in, metadata_key)

        if current_version != expected_version:
            errors.append(
                f"{relative_path} metadata and current contract version disagree: "
                f"{current_version!r} != {expected_version!r}."
            )

        try:
            parse_semver(current_version)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        base_schema = load_base_schema(relative_path)
        if base_schema is None or canonical_json(base_schema) == canonical_json(checked_in):
            continue

        base_version = contract_version(base_schema, metadata_key)
        try:
            old = parse_semver(base_version)
            new = parse_semver(current_version)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        if new <= old:
            errors.append(
                f"Public schema {relative_path} changed without a contract-version bump: "
                f"{base_version} -> {current_version}."
            )

    return errors


def check_validation_profile_version() -> list[str]:
    profile = validation_profile()
    version = profile.get("profile_version")
    if version != VALIDATION_PROFILE_VERSION:
        return ["Validation profile metadata disagrees with VALIDATION_PROFILE_VERSION."]
    try:
        parse_semver(VALIDATION_PROFILE_VERSION)
    except ValueError as exc:
        return [str(exc)]
    return []


def list_base_validation_profile_paths() -> list[Path]:
    """List every validation-profile artifact already present on the PR base branch."""
    base_ref = os.environ.get("GITHUB_BASE_REF")
    if not base_ref:
        return []

    for git_ref in (f"origin/{base_ref}", base_ref):
        result = subprocess.run(
            [
                "git",
                "ls-tree",
                "-r",
                "--name-only",
                git_ref,
                "--",
                "schemas/validation",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return [
                Path(line)
                for line in result.stdout.splitlines()
                if line.strip().endswith(".json")
            ]
    return []


def check_validation_profile_immutability() -> list[str]:
    """Every profile artifact that existed on the base branch is immutable."""
    errors: list[str] = []

    for relative_path in list_base_validation_profile_paths():
        local_path = ROOT / relative_path
        if not local_path.exists():
            errors.append(f"Frozen validation profile artifact was removed: {relative_path}.")
            continue

        base_artifact = load_base_schema(relative_path)
        if base_artifact is None:
            continue

        current = load_json(local_path)
        if canonical_json(base_artifact) != canonical_json(current):
            errors.append(
                "Frozen validation profile artifact changed: "
                f"{relative_path}. Add a new validation profile version instead."
            )
    return errors


def main() -> int:
    errors = [
        *check_generated_artifacts(),
        *check_public_schema_versions(),
        *check_validation_profile_version(),
        *check_validation_profile_immutability(),
    ]
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(
        "Schema artifacts OK: "
        f"record={CURRENT_SCHEMA_VERSION}, validation={VALIDATION_PROFILE_VERSION}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
