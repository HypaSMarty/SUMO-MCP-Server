import time


def test_control_simulation_step_times_out_and_disconnects(monkeypatch) -> None:
    import server as server_module
    import utils.connection as connection_module

    manager = connection_module.SUMOConnection()
    manager._connected = True
    monkeypatch.setattr(server_module, "connection_manager", manager)

    def blocking_simulation_step(_step=0) -> None:
        time.sleep(0.5)

    monkeypatch.setattr(connection_module.traci, "simulationStep", blocking_simulation_step)
    monkeypatch.setattr(connection_module.traci, "close", lambda: None)

    start = time.monotonic()
    result = server_module.control_simulation("step", {"step": 0, "timeout_s": 0.01})
    elapsed = time.monotonic() - start

    assert elapsed < 0.2
    assert "TimeoutError" in result
    assert manager.is_connected() is False

