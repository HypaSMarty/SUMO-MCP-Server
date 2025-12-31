from __future__ import annotations

from pathlib import Path


def test_signal_opt_workflow_falls_back_to_coordinator_on_timeout(
    monkeypatch, tmp_path: Path
) -> None:
    import workflows.signal_opt as signal_opt

    input_net = tmp_path / "input.net.xml"
    input_route = tmp_path / "input.rou.xml"
    input_net.write_text("<net/>", encoding="utf-8")
    input_route.write_text("<routes/>", encoding="utf-8")

    output_dir = tmp_path / "out"

    calls: dict[str, int] = {"cycle": 0, "coord": 0}

    def fake_run_simple_simulation(config_path: str, steps: int = 100) -> str:
        return f"Simulation finished successfully.\nSteps run: {steps}\nconfig={config_path}"

    def fake_analyze_fcd(_fcd_path: str) -> str:
        return "analysis: ok"

    def fake_tls_cycle_adaptation(_net: str, _route: str, _out: str) -> str:
        calls["cycle"] += 1
        return "Error: Command timed out after 300s."

    def fake_tls_coordinator(_net: str, _route: str, out: str, options=None) -> str:
        calls["coord"] += 1
        Path(out).write_text("<additional/>", encoding="utf-8")
        return "tlsCoordinator successful."

    monkeypatch.setattr(signal_opt, "run_simple_simulation", fake_run_simple_simulation)
    monkeypatch.setattr(signal_opt, "analyze_fcd", fake_analyze_fcd)
    monkeypatch.setattr(signal_opt, "tls_cycle_adaptation", fake_tls_cycle_adaptation)
    monkeypatch.setattr(signal_opt, "tls_coordinator", fake_tls_coordinator)

    result = signal_opt.signal_opt_workflow(
        net_file=str(input_net),
        route_file=str(input_route),
        output_dir=str(output_dir),
        steps=10,
        use_coordinator=False,
    )

    assert "Signal Optimization Workflow Completed" in result
    assert "Fell back to: tlsCoordinator" in result
    assert calls["cycle"] == 1
    assert calls["coord"] == 1


def test_signal_opt_workflow_skips_optimization_when_both_methods_fail(
    monkeypatch, tmp_path: Path
) -> None:
    import workflows.signal_opt as signal_opt

    input_net = tmp_path / "input.net.xml"
    input_route = tmp_path / "input.rou.xml"
    input_net.write_text("<net/>", encoding="utf-8")
    input_route.write_text("<routes/>", encoding="utf-8")

    output_dir = tmp_path / "out"

    def fake_run_simple_simulation(_config_path: str, steps: int = 100) -> str:
        return f"Simulation finished successfully.\nSteps run: {steps}"

    def fake_analyze_fcd(_fcd_path: str) -> str:
        return "analysis: ok"

    def fake_tls_cycle_adaptation(_net: str, _route: str, _out: str) -> str:
        return "Error: Command timed out after 300s."

    def fake_tls_coordinator(_net: str, _route: str, _out: str, options=None) -> str:
        return "Error: Command timed out after 300s."

    monkeypatch.setattr(signal_opt, "run_simple_simulation", fake_run_simple_simulation)
    monkeypatch.setattr(signal_opt, "analyze_fcd", fake_analyze_fcd)
    monkeypatch.setattr(signal_opt, "tls_cycle_adaptation", fake_tls_cycle_adaptation)
    monkeypatch.setattr(signal_opt, "tls_coordinator", fake_tls_coordinator)

    result = signal_opt.signal_opt_workflow(
        net_file=str(input_net),
        route_file=str(input_route),
        output_dir=str(output_dir),
        steps=10,
        use_coordinator=False,
    )

    assert "Signal Optimization Workflow Completed" in result
    assert "Optimization was skipped" in result

    optimized_cfg = output_dir / "optimized.sumocfg"
    cfg_text = optimized_cfg.read_text(encoding="utf-8")
    assert '<net-file value="input.net.xml"/>' in cfg_text

