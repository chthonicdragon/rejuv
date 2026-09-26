from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rejuv.models import intervention_episode_json_schema
from rejuv.releases import DataReleaseManifest
from rejuv.sources import SourceManifest
from rejuv.validation import (
    strict_data_release_manifest_schema,
    strict_intervention_episode_schema,
    strict_source_manifest_schema,
    validation_profile,
)


ROOT = Path(__file__).resolve().parents[1]

ARTIFACTS: dict[Path, dict[str, Any]] = {
    Path("schemas/intervention_episode.schema.json"): intervention_episode_json_schema(),
    Path("schemas/source_manifest.schema.json"): SourceManifest.model_json_schema(),
    Path("schemas/data_release_manifest.schema.json"): DataReleaseManifest.model_json_schema(),
    Path("schemas/validation/v0_1_0/intervention_episode.schema.json"): (
        strict_intervention_episode_schema()
    ),
    Path("schemas/validation/v0_1_0/source_manifest.schema.json"): strict_source_manifest_schema(),
    Path("schemas/validation/v0_1_0/data_release_manifest.schema.json"): (
        strict_data_release_manifest_schema()
    ),
    Path("schemas/validation/v0_1_0/profile.json"): validation_profile(),
}


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"


def main() -> None:
    for relative_path, payload in ARTIFACTS.items():
        target = ROOT / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(canonical_json(payload), encoding="utf-8")
        print(target)


if __name__ == "__main__":
    main()
