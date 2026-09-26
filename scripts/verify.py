from __future__ import annotations

import subprocess
from collections.abc import Sequence
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class VerificationStep:
    name: str
    command: tuple[str, ...]


def verification_steps() -> tuple[VerificationStep, ...]:
    python = sys.executable
    return (
        VerificationStep(
            name="schema contract",
            command=(python, "scripts/check_schema_contract.py"),
        ),
        VerificationStep(
            name="public examples",
            command=(python, "scripts/validate_examples.py"),
        ),
        VerificationStep(
            name="ruff",
            command=(python, "-m", "ruff", "check", "."),
        ),
        VerificationStep(
            name="mypy",
            command=(python, "-m", "mypy", "src/rejuv"),
        ),
        VerificationStep(
            name="pytest",
            command=(python, "-m", "pytest"),
        ),
    )


def run_step(step: VerificationStep) -> int:
    print(f"\n==> {step.name}")
    print("$ " + " ".join(step.command))
    completed = subprocess.run(step.command, cwd=ROOT, check=False)
    return completed.returncode


def run(steps: Sequence[VerificationStep] | None = None) -> int:
    selected = tuple(steps) if steps is not None else verification_steps()

    for step in selected:
        return_code = run_step(step)
        if return_code != 0:
            print(f"\nFAILED: {step.name} (exit {return_code})", file=sys.stderr)
            return return_code

    print("\nAll Rejuv verification checks passed.")
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
