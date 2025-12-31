import subprocess


def test_get_sumo_info_passes_timeout(monkeypatch) -> None:
    import server as server_module

    monkeypatch.setattr(server_module, "find_sumo_binary", lambda _: "/usr/bin/sumo")
    monkeypatch.setattr(server_module, "find_sumo_home", lambda: "/tmp/sumo")
    monkeypatch.setattr(server_module, "find_sumo_tools_dir", lambda: "/tmp/sumo/tools")

    captured: dict[str, object] = {}

    def fake_run(cmd, **kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(cmd, 0, stdout="SUMO 1.0\n", stderr="")

    monkeypatch.setattr(server_module.subprocess, "run", fake_run)

    result = server_module.get_sumo_info()
    assert "SUMO Version" in result
    assert captured["timeout"] == 10
    assert captured["capture_output"] is True
    assert captured["text"] is True
    assert captured["check"] is True


def test_get_sumo_info_timeout_expired_is_readable(monkeypatch) -> None:
    import server as server_module

    monkeypatch.setattr(server_module, "find_sumo_binary", lambda _: "/usr/bin/sumo")

    def fake_run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs.get("timeout", 0))

    monkeypatch.setattr(server_module.subprocess, "run", fake_run)

    result = server_module.get_sumo_info()
    assert "timed out" in result.lower()

