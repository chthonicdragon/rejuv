from __future__ import annotations

from types import SimpleNamespace

import scripts.verify as verify


def test_verification_steps_use_current_python() -> None:
    steps = verify.verification_steps()

    assert [step.name for step in steps] == [
        "schema contract",
        "public examples",
        "ruff",
        "mypy",
        "pytest",
    ]
    assert all(step.command[0] == verify.sys.executable for step in steps)


def test_run_stops_on_first_failure(monkeypatch) -> None:
    calls: list[str] = []

    def fake_run(command, *, cwd, check):
        del cwd, check
        calls.append(command[-1])
        return SimpleNamespace(returncode=7 if command[-1] == "second" else 0)

    monkeypatch.setattr(verify.subprocess, "run", fake_run)

    steps = (
        verify.VerificationStep("first", ("python", "first")),
        verify.VerificationStep("second", ("python", "second")),
        verify.VerificationStep("third", ("python", "third")),
    )

    assert verify.run(steps) == 7
    assert calls == ["first", "second"]


def test_run_returns_zero_when_every_step_passes(monkeypatch) -> None:
    def fake_run(command, *, cwd, check):
        del command, cwd, check
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(verify.subprocess, "run", fake_run)

    steps = (verify.VerificationStep("ok", ("python", "ok")),)
    assert verify.run(steps) == 0
