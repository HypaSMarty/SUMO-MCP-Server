import subprocess


def test_subprocess_run_with_timeout_injects_timeout_and_capture_output(monkeypatch) -> None:
    from utils import timeout as timeout_module

    captured: dict[str, object] = {}

    def fake_run(cmd, **kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")

    monkeypatch.setattr(timeout_module.subprocess, "run", fake_run)

    timeout_module.subprocess_run_with_timeout(["echo", "hi"], operation="netconvert", check=True)

    assert "timeout" in captured
    assert captured["capture_output"] is True
    assert captured["text"] is True
    assert captured["check"] is True


def test_subprocess_run_with_timeout_translates_timeout_expired(monkeypatch) -> None:
    from utils import timeout as timeout_module

    def fake_run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs.get("timeout", 0))

    monkeypatch.setattr(timeout_module.subprocess, "run", fake_run)

    try:
        timeout_module.subprocess_run_with_timeout(["echo", "hi"], operation="netconvert", check=True)
    except TimeoutError as exc:
        assert "timed out" in str(exc).lower()
    else:
        raise AssertionError("Expected TimeoutError")


def test_all_mcp_subprocess_tools_use_timeouts(monkeypatch, tmp_path) -> None:
    from mcp_tools import network as network_module
    from mcp_tools import route as route_module
    from mcp_tools import signal as signal_module
    from utils import timeout as timeout_module

    calls: list[dict[str, object]] = []

    def fake_run(cmd, **kwargs):
        calls.append({"cmd": cmd, "kwargs": kwargs})
        return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")

    monkeypatch.setattr(timeout_module.subprocess, "run", fake_run)

    monkeypatch.setattr(network_module.sumolib, "checkBinary", lambda _: "/usr/bin/fake")
    monkeypatch.setattr(route_module.sumolib, "checkBinary", lambda _: "/usr/bin/fake")

    monkeypatch.setattr(network_module, "find_sumo_tool_script", lambda _: "osmGet.py")
    monkeypatch.setattr(route_module, "find_sumo_tool_script", lambda _: "randomTrips.py")
    monkeypatch.setattr(signal_module, "find_sumo_tool_script", lambda _: "tlsTool.py")

    out_dir = tmp_path / "osm_out"

    network_module.netconvert("in.osm.xml", "out.net.xml")
    network_module.netgenerate("out.net.xml", grid=True, grid_number=3)
    network_module.osm_get("0,0,1,1", str(out_dir))

    route_module.random_trips("net.net.xml", "trips.trips.xml", end_time=1000)
    route_module.duarouter("net.net.xml", "trips.trips.xml", "routes.rou.xml")
    route_module.od2trips("od.xml", "trips.trips.xml")

    signal_module.tls_cycle_adaptation("net.net.xml", "routes.rou.xml", "out.net.xml")
    signal_module.tls_coordinator("net.net.xml", "routes.rou.xml", "out.net.xml")

    assert calls, "Expected at least one subprocess invocation"
    for call in calls:
        kwargs = call["kwargs"]
        assert "timeout" in kwargs
        assert kwargs.get("capture_output") is True

