from __future__ import annotations

from pathlib import Path

from ctxkeeper import main


def test_first_run_launches_wizard_instead_of_server(monkeypatch, tmp_path: Path) -> None:
    calls: list[str] = []
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main, "run_configuration_wizard", lambda path: calls.append(f"wizard:{Path(path).name}"))
    monkeypatch.setattr(main, "run_contextkeeper", lambda: calls.append("server"))

    main.run([])

    assert calls == ["wizard:contextkeeper.yaml"]


def test_existing_configuration_bypasses_wizard_and_starts_server(monkeypatch, tmp_path: Path) -> None:
    calls: list[str] = []
    monkeypatch.chdir(tmp_path)
    (tmp_path / "contextkeeper.yaml").write_text("server:\n  port: 11500\n", encoding="utf-8")
    monkeypatch.setattr(main, "run_configuration_wizard", lambda path: calls.append("wizard"))
    monkeypatch.setattr(main, "run_contextkeeper", lambda: calls.append("server"))

    main.run([])

    assert calls == ["server"]


def test_configure_option_launches_wizard_even_when_configuration_exists(monkeypatch, tmp_path: Path) -> None:
    calls: list[str] = []
    monkeypatch.chdir(tmp_path)
    (tmp_path / "contextkeeper.yaml").write_text("server:\n  port: 11500\n", encoding="utf-8")
    monkeypatch.setattr(main, "run_configuration_wizard", lambda path: calls.append(f"wizard:{Path(path).name}"))
    monkeypatch.setattr(main, "run_contextkeeper", lambda: calls.append("server"))

    main.run(["--configure"])

    assert calls == ["wizard:contextkeeper.yaml"]
