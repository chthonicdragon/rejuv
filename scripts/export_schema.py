from __future__ import annotations

import json
from pathlib import Path

from rejuv.models import intervention_episode_json_schema


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "schemas" / "intervention_episode.schema.json"


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    payload = intervention_episode_json_schema()
    TARGET.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(TARGET)


if __name__ == "__main__":
    main()
