from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from rejuv.models import InterventionEpisode
from rejuv.releases import DataReleaseManifest
from rejuv.sources import SourceManifest
from rejuv.validation import (
    validate_data_release_manifest,
    validate_intervention_episode,
    validate_source_manifest,
)


ROOT = Path(__file__).resolve().parents[1]

EXAMPLES: tuple[tuple[Path, type[Any], Any], ...] = (
    (
        ROOT / "examples" / "intervention_episode.synthetic.json",
        InterventionEpisode,
        validate_intervention_episode,
    ),
    (
        ROOT / "examples" / "source_manifest.synthetic.json",
        SourceManifest,
        validate_source_manifest,
    ),
    (
        ROOT / "examples" / "data_release_manifest.synthetic.json",
        DataReleaseManifest,
        validate_data_release_manifest,
    ),
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_examples() -> list[str]:
    errors: list[str] = []

    for path, model, validator in EXAMPLES:
        try:
            payload = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: cannot load JSON: {exc}")
            continue

        try:
            model.model_validate(payload)
        except ValidationError as exc:
            errors.append(f"{path.relative_to(ROOT)}: Pydantic validation failed: {exc}")

        report = validator(payload)
        if not report.valid:
            details = "; ".join(f"{issue.code}@{issue.path}" for issue in report.issues)
            errors.append(f"{path.relative_to(ROOT)}: validation profile failed: {details}")

    return errors


def main() -> int:
    errors = validate_examples()
    if errors:
        print("Public example validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(EXAMPLES)} public examples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
