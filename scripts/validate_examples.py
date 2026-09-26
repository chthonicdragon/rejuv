from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from pydantic import ValidationError

from rejuv.models import InterventionEpisode
from rejuv.releases import DataReleaseManifest
from rejuv.sources import SourceManifest


ROOT = Path(__file__).resolve().parents[1]
INTERVENTION_SCHEMA = ROOT / "schemas" / "intervention_episode.schema.json"

EXAMPLES: tuple[tuple[Path, type[Any]], ...] = (
    (ROOT / "examples" / "intervention_episode.synthetic.json", InterventionEpisode),
    (ROOT / "examples" / "source_manifest.synthetic.json", SourceManifest),
    (ROOT / "examples" / "data_release_manifest.synthetic.json", DataReleaseManifest),
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_examples() -> list[str]:
    errors: list[str] = []

    for path, model in EXAMPLES:
        try:
            payload = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: cannot load JSON: {exc}")
            continue

        try:
            model.model_validate(payload)
        except ValidationError as exc:
            errors.append(f"{path.relative_to(ROOT)}: Pydantic validation failed: {exc}")
            continue

        if model is InterventionEpisode:
            try:
                schema = load_json(INTERVENTION_SCHEMA)
                Draft202012Validator(schema).validate(payload)
            except Exception as exc:
                errors.append(
                    f"{path.relative_to(ROOT)}: JSON Schema validation failed: {exc}"
                )

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
