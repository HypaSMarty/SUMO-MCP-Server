import time
import threading

from unittest.mock import patch


def test_run_simple_simulation_times_out_and_closes_traci(tmp_path) -> None:
    from mcp_tools import simulation as simulation_module
    from utils.timeout import TIMEOUT_CONFIGS, TimeoutConfig

    config_path = tmp_path / "dummy.sumocfg"
    config_path.write_text("<configuration/>", encoding="utf-8")

    with patch.dict(
        TIMEOUT_CONFIGS,
        {
            "simulation": TimeoutConfig(
                base_timeout=0.1,
                max_timeout=0.1,
                backoff_factor=2.0,
                heartbeat_interval=0.1,
            )
        },
        clear=False,
    ):
        with patch.object(simulation_module, "find_sumo_binary", return_value="/usr/bin/sumo"):
            close_threads: list[str] = []

            def fake_step(*_a, **_k) -> None:
                time.sleep(0.5)

            def fake_close(*_a, **_k) -> None:
                close_threads.append(threading.current_thread().name)

            with (
                patch.object(simulation_module.traci, "start", lambda *a, **k: None),
                patch.object(simulation_module.traci, "simulationStep", fake_step),
                patch.object(simulation_module.traci.vehicle, "getIDCount", lambda *a, **k: 0),
                patch.object(simulation_module.traci, "close", fake_close),
            ):
                start = time.monotonic()
                result = simulation_module.run_simple_simulation(str(config_path), steps=1)
                elapsed = time.monotonic() - start

    assert elapsed < 0.3
    assert "TimeoutError" in result
    # Best-effort cleanup is attempted without risking an indefinite hang.
    assert any("traci.close" in name for name in close_threads)
