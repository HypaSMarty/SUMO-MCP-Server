import os
import sys
import subprocess
import json
import shutil
import time
import selectors
from pathlib import Path
from typing import Any

import pytest

# This module runs real SUMO simulations/tools. Skip in environments without SUMO.
HAS_SUMO = bool(os.environ.get("SUMO_HOME")) or shutil.which("sumo") is not None
pytestmark = pytest.mark.skipif(
    not HAS_SUMO,
    reason="Requires SUMO installed (set SUMO_HOME or add `sumo` to PATH).",
)


def _read_json_line(process: subprocess.Popen[str], timeout_s: float = 300.0) -> dict[str, Any]:
    if process.stdout is None:
        raise RuntimeError("process.stdout is None")

    # Windows pipes do not support selectors/select reliably.
    if sys.platform == "win32":
        import queue
        import threading

        deadline = time.time() + timeout_s
        while time.time() < deadline:
            remaining = deadline - time.time()
            line_queue: queue.Queue[str] = queue.Queue(maxsize=1)

            def reader() -> None:
                line_queue.put(process.stdout.readline())

            thread = threading.Thread(target=reader, daemon=True)
            thread.start()

            try:
                line = line_queue.get(timeout=remaining)
            except queue.Empty:
                raise TimeoutError("timed out waiting for server JSON-RPC response") from None

            if not line:
                raise RuntimeError("server stdout closed unexpectedly")

            line = line.strip()
            if not line:
                continue

            try:
                return json.loads(line)
            except json.JSONDecodeError as exc:
                raise AssertionError(f"Expected JSON-RPC line, got: {line}") from exc

        raise TimeoutError("timed out waiting for server JSON-RPC response")

    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    try:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            remaining = deadline - time.time()
            events = selector.select(timeout=remaining)
            if not events:
                continue

            line = process.stdout.readline()
            if not line:
                raise RuntimeError("server stdout closed unexpectedly")

            line = line.strip()
            if not line:
                continue

            try:
                return json.loads(line)
            except json.JSONDecodeError as exc:
                raise AssertionError(f"Expected JSON-RPC line, got: {line}") from exc

        raise TimeoutError("timed out waiting for server JSON-RPC response")
    finally:
        selector.close()


def test_signal_opt_workflow(tmp_path: Path) -> None:
    # Setup paths
    base_dir = Path(__file__).resolve().parent
    fixtures_dir = tmp_path / "fixtures" / "simple_sim"
    output_dir = tmp_path / "output_signal_opt"

    fixtures_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    net_file = fixtures_dir / "hello.net.xml"
    trips_file = fixtures_dir / "hello.trips.xml"
    route_file = fixtures_dir / "hello.rou.xml"
    
    # Ensure fixtures exist (re-run generation commands if needed)
    # Ideally we should use the tools we just implemented, but we are testing the server wrapper.
    # Let's use the server to run the workflow which takes existing files.
    
    # For this test, let's assume fixtures exist or use the ones from previous turn.
    # If not, we might fail. Let's make sure they exist.
    # We can use our new tools code directly to generate them for testing.
    from mcp_tools.network import netgenerate
    from mcp_tools.route import random_trips, duarouter
    
    res_net = netgenerate(str(net_file), grid=True, grid_number=3, options=["--tls.guess"])
    assert "error" not in res_net.lower() and "failed" not in res_net.lower()
    res_trips = random_trips(str(net_file), str(trips_file), end_time=50)
    assert "error" not in res_trips.lower() and "failed" not in res_trips.lower()
    res_routes = duarouter(str(net_file), str(trips_file), str(route_file))
    assert "error" not in res_routes.lower() and "failed" not in res_routes.lower()
    
    # Now run the workflow via server script (integration test)
    server_path = base_dir.parent / "src" / "server.py"
    python_exe = sys.executable # Use current python

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    process = subprocess.Popen(
        [python_exe, str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        text=True,
        env=env,
        bufsize=1,
    )

    try:
        assert process.stdin is not None

        # Initialize
        process.stdin.write(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "pytest", "version": "0"},
                    },
                }
            )
            + "\n"
        )
        process.stdin.flush()
        init_resp = _read_json_line(process, timeout_s=20.0)
        assert init_resp["id"] == 1

        process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        process.stdin.flush()

        # Call Workflow
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "run_workflow",
                "arguments": {
                    "workflow_name": "signal_opt",
                    "params": {
                        "net_file": str(net_file),
                        "route_file": str(route_file),
                        "output_dir": str(output_dir),
                        "steps": 50,
                        "use_coordinator": False,
                    },
                },
            },
        }
        process.stdin.write(json.dumps(req) + "\n")
        process.stdin.flush()

        response = _read_json_line(process, timeout_s=900.0)  # 15 minutes for signal_opt workflow

        if "error" in response:
            raise AssertionError(f"Server returned error: {response['error']}")

        content = response["result"]["content"][0]["text"]
        assert "Signal Optimization Workflow Completed" in content
        assert "Baseline Results" in content
        assert "Optimized Results" in content
        # If optimization was skipped (P0-15 fallback), this test should fail to
        # avoid silently passing without actually validating TLS optimization.
        assert "Optimization was skipped" not in content
    finally:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    test_signal_opt_workflow()
