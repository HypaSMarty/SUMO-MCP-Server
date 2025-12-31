import subprocess


def test_tls_cycle_adaptation_passes_size_params(monkeypatch, tmp_path) -> None:
    from mcp_tools import signal as signal_module

    net_file = tmp_path / "net.net.xml"
    route_file = tmp_path / "routes.rou.xml"
    net_file.write_text("<net></net>", encoding="utf-8")
    route_file.write_text("<routes></routes>", encoding="utf-8")

    monkeypatch.setattr(signal_module, "find_sumo_tool_script", lambda _: "tlsCycleAdaptation.py")

    captured: dict[str, object] = {}

    def fake_run(cmd, operation: str, params=None, **kwargs):
        captured["operation"] = operation
        captured["params"] = params
        return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")

    monkeypatch.setattr(signal_module, "subprocess_run_with_timeout", fake_run)

    result = signal_module.tls_cycle_adaptation(str(net_file), str(route_file), str(tmp_path / "out.net.xml"))

    assert "successful" in result.lower()
    assert captured["operation"] == "tlsCycleAdaptation"
    params = captured["params"]
    assert isinstance(params, dict)
    assert params.get("route_files_bytes") == route_file.stat().st_size
    assert params.get("net_file_bytes") == net_file.stat().st_size

