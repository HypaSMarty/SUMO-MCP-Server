import subprocess


def test_ensure_traci_start_stdout_suppressed_injects_default(monkeypatch) -> None:
    import traci

    captured: dict[str, object] = {}

    def fake_start(cmd, *args, **kwargs):
        captured["stdout"] = kwargs.get("stdout")
        return None

    monkeypatch.setattr(traci, "start", fake_start)

    from utils.traci import ensure_traci_start_stdout_suppressed

    ensure_traci_start_stdout_suppressed()
    traci.start(["sumo"])

    assert captured["stdout"] is subprocess.DEVNULL


def test_ensure_traci_start_stdout_suppressed_does_not_override(monkeypatch) -> None:
    import traci

    captured: dict[str, object] = {}

    def fake_start(cmd, *args, **kwargs):
        captured["stdout"] = kwargs.get("stdout")
        return None

    monkeypatch.setattr(traci, "start", fake_start)

    from utils.traci import ensure_traci_start_stdout_suppressed

    ensure_traci_start_stdout_suppressed()

    custom_stdout = object()
    traci.start(["sumo"], stdout=custom_stdout)

    assert captured["stdout"] is custom_stdout


def test_ensure_traci_start_stdout_suppressed_is_idempotent(monkeypatch) -> None:
    import traci

    def fake_start(cmd, *args, **kwargs):
        return None

    monkeypatch.setattr(traci, "start", fake_start)

    from utils.traci import ensure_traci_start_stdout_suppressed

    ensure_traci_start_stdout_suppressed()
    first = traci.start
    ensure_traci_start_stdout_suppressed()
    second = traci.start

    assert first is second


def test_ensure_traci_start_stdout_suppressed_noop_when_unsupported(monkeypatch) -> None:
    import traci

    def fake_start(cmd):
        return None

    monkeypatch.setattr(traci, "start", fake_start)

    from utils.traci import ensure_traci_start_stdout_suppressed

    ensure_traci_start_stdout_suppressed()
    assert traci.start is fake_start

