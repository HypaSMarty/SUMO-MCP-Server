#!/usr/bin/env python3
"""
Traffic Signal Addition and Optimization Scenario (Robust Version)

This script demonstrates a complete workflow:
1. Generate a grid network with traffic lights
2. Generate traffic demand
3. Run baseline simulation
4. Optimize traffic light timings
5. Run optimized simulation
6. Compare results

Features:
- Automatic error recovery
- Detailed progress logging
- Performance metrics comparison
- ASCII-only output (no emoji)
"""

import os
import sys
import shutil
import time
from typing import List, Optional

# Add src to path for direct execution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
sys.path.insert(0, SRC_DIR)

from mcp_tools.network import netgenerate
from mcp_tools.route import random_trips, duarouter
from mcp_tools.signal import tls_cycle_adaptation
from mcp_tools.simulation import run_simple_simulation
from mcp_tools.analysis import analyze_fcd


class SignalOptimizationScenario:
    """Manages a complete signal optimization workflow."""

    def __init__(self, output_dir: str):
        """Initialize scenario with output directory."""
        self.output_dir = output_dir
        self.config = {
            'grid_size': 4,
            'simulation_steps': 1800,
            'traffic_period': 2.0,
        }

        # File paths
        self.net_file = os.path.join(output_dir, "grid.net.xml")
        self.trips_file = os.path.join(output_dir, "trips.xml")
        self.routes_file = os.path.join(output_dir, "routes.xml")
        self.baseline_cfg = os.path.join(output_dir, "baseline.sumocfg")
        self.baseline_fcd = os.path.join(output_dir, "baseline_fcd.xml")
        self.optimized_net = os.path.join(output_dir, "optimized.net.xml")
        self.optimized_cfg = os.path.join(output_dir, "optimized.sumocfg")
        self.optimized_fcd = os.path.join(output_dir, "optimized_fcd.xml")

    def print_header(self, text: str, level: int = 1) -> None:
        """Print formatted header."""
        if level == 1:
            print(f"\n{'='*70}")
            print(f"  {text}")
            print('='*70)
        else:
            print(f"\n[Step {level}] {text}")
            print('-'*70)

    def print_status(self, message: str, success: bool = True) -> None:
        """Print status message."""
        prefix = "[OK]  " if success else "[FAIL]"
        print(f"{prefix} {message}")

    def step1_generate_network(self) -> bool:
        """Generate grid network with traffic lights."""
        self.print_header("Generate Grid Network", level=1)

        result = netgenerate(
            self.net_file,
            grid=True,
            grid_number=self.config['grid_size'],
            options=[
                "--default.lanenumber", "2",
                "--default.speed", "13.89",
                "--tls.guess", "true",
            ]
        )

        if "successful" not in result.lower():
            self.print_status(f"Network generation failed: {result}", False)
            return False

        self.print_status(f"Network created: {os.path.basename(self.net_file)}")

        # Count traffic lights
        try:
            with open(self.net_file, 'r', encoding='utf-8') as f:
                tls_count = f.read().count('<tlLogic')
            self.print_status(f"Traffic lights: {tls_count}")
        except Exception:
            pass

        return True

    def step2_generate_demand(self) -> bool:
        """Generate traffic demand."""
        self.print_header("Generate Traffic Demand", level=2)

        result = random_trips(
            self.net_file,
            self.trips_file,
            end_time=self.config['simulation_steps'],
            period=self.config['traffic_period'],
            options=["--fringe-factor", "5"]
        )

        if "successful" not in result.lower():
            self.print_status(f"Trip generation failed: {result}", False)
            return False

        self.print_status(f"Trips created: {os.path.basename(self.trips_file)}")

        # Count trips
        try:
            with open(self.trips_file, 'r', encoding='utf-8') as f:
                trips_count = f.read().count('<trip ')
            self.print_status(f"Total trips: {trips_count}")
        except Exception:
            pass

        return True

    def step3_compute_routes(self) -> bool:
        """Compute vehicle routes."""
        self.print_header("Compute Routes", level=3)

        result = duarouter(self.net_file, self.trips_file, self.routes_file)

        if "successful" not in result.lower():
            self.print_status(f"Route computation failed: {result}", False)
            return False

        self.print_status(f"Routes computed: {os.path.basename(self.routes_file)}")
        return True

    def step4_baseline_simulation(self) -> bool:
        """Run baseline simulation."""
        self.print_header("Baseline Simulation", level=4)

        self._create_config(
            self.baseline_cfg,
            self.net_file,
            self.routes_file,
            self.baseline_fcd,
            self.config['simulation_steps']
        )

        result = run_simple_simulation(
            self.baseline_cfg,
            self.config['simulation_steps']
        )

        if "error" in result.lower() or not os.path.exists(self.baseline_fcd):
            self.print_status(f"Simulation failed: {result}", False)
            return False

        self.print_status("Baseline simulation completed")
        print(result)

        # Analyze results
        analysis = analyze_fcd(self.baseline_fcd)
        print("\n--- Baseline Performance ---")
        print(analysis)

        return True

    def step5_optimize_signals(self) -> bool:
        """Optimize traffic light timings."""
        self.print_header("Optimize Traffic Signals", level=5)

        result = tls_cycle_adaptation(
            self.net_file,
            self.routes_file,
            self.optimized_net
        )

        if "successful" not in result.lower():
            self.print_status(f"Optimization failed: {result}", False)
            # Fallback: use original network
            self.print_status("Using original network as fallback", False)
            shutil.copy2(self.net_file, self.optimized_net)
            return True  # Continue with original network

        self.print_status("Signal timings optimized")
        if self._is_additional_file(self.optimized_net):
            self.print_status(f"Optimized TLS program: {os.path.basename(self.optimized_net)}")
        else:
            self.print_status(f"Optimized network: {os.path.basename(self.optimized_net)}")

        return True

    def step6_optimized_simulation(self) -> bool:
        """Run optimized simulation."""
        self.print_header("Optimized Simulation", level=6)

        # Ensure optimized network exists
        if not os.path.exists(self.optimized_net):
            self.print_status("Optimized network not found, using original", False)
            shutil.copy2(self.net_file, self.optimized_net)

        additional_files: Optional[List[str]] = None
        net_for_optimized_sim = self.optimized_net
        if self._is_additional_file(self.optimized_net):
            additional_files = [self.optimized_net]
            net_for_optimized_sim = self.net_file

        self._create_config(
            self.optimized_cfg,
            net_for_optimized_sim,
            self.routes_file,
            self.optimized_fcd,
            self.config['simulation_steps'],
            additional_files=additional_files,
        )

        # Add small delay to ensure file system sync
        time.sleep(0.5)

        result = run_simple_simulation(
            self.optimized_cfg,
            self.config['simulation_steps']
        )

        if "error" in result.lower() or not os.path.exists(self.optimized_fcd):
            self.print_status(f"Simulation failed: {result}", False)
            return False

        self.print_status("Optimized simulation completed")
        print(result)

        # Analyze results
        analysis = analyze_fcd(self.optimized_fcd)
        print("\n--- Optimized Performance ---")
        print(analysis)

        return True

    def step7_compare_results(self) -> None:
        """Compare baseline and optimized results."""
        self.print_header("Performance Comparison", level=7)

        if not os.path.exists(self.baseline_fcd) or not os.path.exists(self.optimized_fcd):
            self.print_status("Cannot compare: missing FCD files", False)
            return

        try:
            baseline_stats = self._extract_stats(self.baseline_fcd)
            optimized_stats = self._extract_stats(self.optimized_fcd)

            if baseline_stats and optimized_stats:
                self._print_comparison(baseline_stats, optimized_stats)
            else:
                self.print_status("Could not extract statistics", False)
        except Exception as e:
            self.print_status(f"Comparison failed: {e}", False)

    def run(self) -> int:
        """Execute complete scenario."""
        self.print_header("Traffic Signal Optimization Scenario")
        print(f"\nConfiguration:")
        print(f"  Grid size: {self.config['grid_size']}x{self.config['grid_size']}")
        print(f"  Simulation: {self.config['simulation_steps']}s")
        print(f"  Traffic period: {self.config['traffic_period']}s/vehicle")
        print(f"\nOutput directory: {self.output_dir}")

        try:
            # Execute workflow steps
            steps = [
                (self.step1_generate_network, "Network generation"),
                (self.step2_generate_demand, "Demand generation"),
                (self.step3_compute_routes, "Route computation"),
                (self.step4_baseline_simulation, "Baseline simulation"),
                (self.step5_optimize_signals, "Signal optimization"),
                (self.step6_optimized_simulation, "Optimized simulation"),
            ]

            for step_func, step_name in steps:
                if not step_func():
                    self.print_status(f"Workflow stopped at: {step_name}", False)
                    return 1

            # Comparison (non-critical)
            self.step7_compare_results()

            # Success summary
            self.print_header("Scenario Completed Successfully")
            print(f"\nAll files saved to: {self.output_dir}")
            print("\nKey outputs:")
            print(f"  Network:         {os.path.basename(self.net_file)}")
            print(f"  Routes:          {os.path.basename(self.routes_file)}")
            print(f"  Baseline FCD:    {os.path.basename(self.baseline_fcd)}")
            print(f"  Optimized FCD:   {os.path.basename(self.optimized_fcd)}")

            return 0

        except KeyboardInterrupt:
            self.print_status("Interrupted by user", False)
            return 130
        except Exception as e:
            self.print_status(f"Unexpected error: {e}", False)
            import traceback
            traceback.print_exc()
            return 1

    def _create_config(
        self,
        cfg_path: str,
        net_file: str,
        route_file: str,
        fcd_file: str,
        steps: int,
        additional_files: Optional[List[str]] = None,
    ) -> None:
        """Create SUMO configuration file."""
        cfg_dir = os.path.dirname(os.path.abspath(cfg_path))

        def relpath(path: str) -> str:
            try:
                return os.path.relpath(path, cfg_dir)
            except ValueError:
                return os.path.basename(path)

        additional_str = ""
        if additional_files:
            val = ",".join(relpath(p) for p in additional_files)
            additional_str = f'        <additional-files value="{val}"/>\n'

        with open(cfg_path, 'w', encoding='utf-8') as f:
            f.write(f"""<configuration>
    <input>
        <net-file value="{relpath(net_file)}"/>
        <route-files value="{relpath(route_file)}"/>
{additional_str.rstrip()}
    </input>
    <time>
        <begin value="0"/>
        <end value="{steps}"/>
    </time>
    <output>
        <fcd-output value="{os.path.basename(fcd_file)}"/>
    </output>
    <processing>
        <time-to-teleport value="300"/>
    </processing>
    <report>
        <no-step-log value="true"/>
    </report>
</configuration>""")

    def _is_additional_file(self, file_path: str) -> bool:
        """Return True if the file looks like a SUMO additional file (root <additional>)."""
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                head = f.read(1000)
            return '<additional' in head
        except OSError:
            return False

    def _extract_stats(self, fcd_file: str) -> dict:
        """Extract statistics from FCD file."""
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(fcd_file)
            root = tree.getroot()

            speeds = []
            vehicles = set()

            for timestep in root.findall('timestep'):
                for vehicle in timestep.findall('vehicle'):
                    vid = vehicle.get('id')
                    speed = vehicle.get('speed')

                    if vid:
                        vehicles.add(vid)
                    if speed:
                        try:
                            speeds.append(float(speed))
                        except ValueError:
                            pass

            return {
                'avg_speed': sum(speeds) / len(speeds) if speeds else 0,
                'vehicle_count': len(vehicles),
                'data_points': len(speeds)
            }
        except Exception:
            return {}

    def _print_comparison(self, baseline: dict, optimized: dict) -> None:
        """Print performance comparison."""
        print("\n" + "="*70)
        print("PERFORMANCE COMPARISON")
        print("="*70)

        b_speed = baseline.get('avg_speed', 0)
        o_speed = optimized.get('avg_speed', 0)
        improvement = ((o_speed - b_speed) / b_speed * 100) if b_speed > 0 else 0

        print(f"\nAverage Speed:")
        print(f"  Baseline:  {b_speed:.2f} m/s")
        print(f"  Optimized: {o_speed:.2f} m/s")
        print(f"  Change:    {improvement:+.2f}%")

        if improvement > 2:
            print("\n[+] Significant improvement detected")
        elif improvement < -2:
            print("\n[-] Performance degradation detected")
        else:
            print("\n[~] Minimal change")

        print(f"\nVehicle Count:")
        print(f"  Baseline:  {baseline.get('vehicle_count', 0)}")
        print(f"  Optimized: {optimized.get('vehicle_count', 0)}")
        print("\n" + "="*70)


def main() -> int:
    """Main entry point."""
    # Create output directory
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("examples", f"signal_opt_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    # Run scenario
    scenario = SignalOptimizationScenario(output_dir)
    return scenario.run()


if __name__ == "__main__":
    sys.exit(main())
