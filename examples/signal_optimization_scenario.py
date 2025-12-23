#!/usr/bin/env python3
"""
Traffic Signal Addition and Optimization Scenario

This script demonstrates a complete workflow:
1. Generate a grid network
2. Add traffic lights to key intersections
3. Generate traffic demand
4. Run baseline simulation
5. Optimize traffic light timings
6. Run optimized simulation
7. Compare results

No SUMO_HOME dependency for network generation binaries,
but SUMO_HOME required for Python tool scripts (randomTrips.py, tls*.py).
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path

# Add src to path for direct execution
# Script is in examples/, so src is in parent directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
sys.path.insert(0, SRC_DIR)

from mcp_tools.network import netgenerate
from mcp_tools.route import random_trips, duarouter
from mcp_tools.signal import tls_cycle_adaptation
from mcp_tools.simulation import run_simple_simulation
from mcp_tools.analysis import analyze_fcd


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def print_step(step: int, description: str) -> None:
    """Print a step description."""
    print(f"\n[Step {step}] {description}")
    print('-' * 70)


def print_result(result: str, success: bool = True) -> None:
    """Print operation result."""
    prefix = "[OK]" if success else "[FAIL]"
    print(f"{prefix} {result}")


def create_output_dir(base_name: str) -> str:
    """Create a timestamped output directory."""
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("examples", f"{base_name}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def main() -> int:
    """Run the complete traffic signal optimization scenario."""

    print_section("Traffic Signal Addition and Optimization Scenario")
    print("This scenario demonstrates:")
    print("  - Grid network generation with traffic lights")
    print("  - Traffic demand generation")
    print("  - Baseline simulation")
    print("  - Signal timing optimization")
    print("  - Performance comparison")

    # Configuration
    GRID_SIZE = 4  # 4x4 grid network
    SIMULATION_STEPS = 1800  # 30 minutes (1800 seconds)
    TRAFFIC_PERIOD = 2.0  # Average 2 seconds between vehicles

    # Create output directory
    output_dir = create_output_dir("signal_optimization")
    print(f"\nOutput directory: {output_dir}")

    # File paths
    net_file = os.path.join(output_dir, "grid.net.xml")
    trips_file = os.path.join(output_dir, "trips.xml")
    routes_file = os.path.join(output_dir, "routes.xml")
    baseline_cfg = os.path.join(output_dir, "baseline.sumocfg")
    baseline_fcd = os.path.join(output_dir, "baseline_fcd.xml")
    optimized_net = os.path.join(output_dir, "optimized.net.xml")
    optimized_cfg = os.path.join(output_dir, "optimized.sumocfg")
    optimized_fcd = os.path.join(output_dir, "optimized_fcd.xml")

    try:
        # ================================================================
        # STEP 1: Generate Grid Network with Traffic Lights
        # ================================================================
        print_step(1, "Generate grid network with traffic lights")

        result = netgenerate(
            net_file,
            grid=True,
            grid_number=GRID_SIZE,
            options=[
                "--default.lanenumber", "2",           # 2 lanes per direction
                "--default.speed", "13.89",            # 50 km/h
                "--tls.guess", "true",                 # Auto-add traffic lights
                "--tls.guess.threshold", "5",          # Min 5 edges for TLS
                "--no-turnarounds", "false",           # Allow U-turns
            ]
        )

        if "successful" in result.lower():
            print_result(f"Network generated: {net_file}")

            # Count traffic lights
            try:
                with open(net_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tls_count = content.count('<tlLogic')
                print_result(f"Traffic lights created: {tls_count}")
            except Exception as e:
                print_result(f"Could not count traffic lights: {e}", success=False)
        else:
            print_result(f"Network generation failed: {result}", success=False)
            return 1

        # ================================================================
        # STEP 2: Generate Traffic Demand
        # ================================================================
        print_step(2, "Generate random traffic demand")

        result = random_trips(
            net_file,
            trips_file,
            end_time=SIMULATION_STEPS,
            period=TRAFFIC_PERIOD,
            options=["--fringe-factor", "5"]  # More traffic from edges
        )

        if "successful" in result.lower():
            print_result(f"Trips generated: {trips_file}")

            # Count trips
            try:
                with open(trips_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    trips_count = content.count('<trip ')
                print_result(f"Total trips: {trips_count}")
            except Exception as e:
                print_result(f"Could not count trips: {e}", success=False)
        else:
            print_result(f"Trip generation failed: {result}", success=False)
            return 1

        # ================================================================
        # STEP 3: Compute Routes
        # ================================================================
        print_step(3, "Compute vehicle routes")

        result = duarouter(
            net_file,
            trips_file,
            routes_file,
            options=[]  # Use default options
        )

        if "successful" in result.lower():
            print_result(f"Routes computed: {routes_file}")
        else:
            print_result(f"Route computation failed: {result}", success=False)
            return 1

        # ================================================================
        # STEP 4: Run Baseline Simulation
        # ================================================================
        print_step(4, "Run baseline simulation (original traffic lights)")

        # Create baseline config
        _create_simple_config(
            baseline_cfg,
            net_file,
            routes_file,
            baseline_fcd,
            SIMULATION_STEPS
        )

        result = run_simple_simulation(baseline_cfg, SIMULATION_STEPS)

        if "successful" in result.lower():
            print_result("Baseline simulation completed")
            print(result)

            # Analyze baseline results
            analysis = analyze_fcd(baseline_fcd)
            print("\n--- Baseline Performance ---")
            print(analysis)
        else:
            print_result(f"Baseline simulation failed: {result}", success=False)
            return 1

        # ================================================================
        # STEP 5: Optimize Traffic Light Timings
        # ================================================================
        print_step(5, "Optimize traffic light timings based on traffic demand")

        result = tls_cycle_adaptation(net_file, routes_file, optimized_net)

        if "successful" in result.lower():
            print_result(f"Optimized network saved: {optimized_net}")
            print_result("Signal timings adapted to traffic demand")
        else:
            print_result(f"Signal optimization failed: {result}", success=False)
            # Try to continue with original network
            print_result("Continuing with original network...", success=False)
            shutil.copy2(net_file, optimized_net)

        # ================================================================
        # STEP 6: Run Optimized Simulation
        # ================================================================
        print_step(6, "Run optimized simulation (adapted traffic lights)")

        # Create optimized config
        _create_simple_config(
            optimized_cfg,
            optimized_net,
            routes_file,
            optimized_fcd,
            SIMULATION_STEPS
        )

        result = run_simple_simulation(optimized_cfg, SIMULATION_STEPS)

        if "successful" in result.lower():
            print_result("Optimized simulation completed")
            print(result)

            # Analyze optimized results
            analysis = analyze_fcd(optimized_fcd)
            print("\n--- Optimized Performance ---")
            print(analysis)
        else:
            print_result(f"Optimized simulation failed: {result}", success=False)
            return 1

        # ================================================================
        # STEP 7: Compare Results
        # ================================================================
        print_step(7, "Compare baseline vs. optimized performance")

        comparison = _compare_results(baseline_fcd, optimized_fcd)
        print(comparison)

        # ================================================================
        # Summary
        # ================================================================
        print_section("Scenario Completed Successfully")
        print(f"\nAll output files saved to: {output_dir}")
        print("\nKey files:")
        print(f"  - Network: {net_file}")
        print(f"  - Routes: {routes_file}")
        print(f"  - Baseline config: {baseline_cfg}")
        print(f"  - Optimized config: {optimized_cfg}")
        print(f"  - Baseline FCD: {baseline_fcd}")
        print(f"  - Optimized FCD: {optimized_fcd}")

        print("\nNext steps:")
        print("  1. Visualize results: sumo-gui -c baseline.sumocfg")
        print("  2. Compare FCD data with your analysis tools")
        print("  3. Adjust traffic demand and re-run optimization")

        return 0

    except KeyboardInterrupt:
        print_result("\nScenario interrupted by user", success=False)
        return 130
    except Exception as e:
        print_result(f"\nUnexpected error: {e}", success=False)
        import traceback
        traceback.print_exc()
        return 1


def _create_simple_config(
    cfg_path: str,
    net_file: str,
    route_file: str,
    fcd_file: str,
    steps: int
) -> None:
    """Create a simple SUMO configuration file."""

    cfg_dir = os.path.dirname(os.path.abspath(cfg_path))

    def _relpath(file_path: str) -> str:
        """Get relative path if possible."""
        try:
            return os.path.relpath(file_path, cfg_dir)
        except ValueError:
            return os.path.basename(file_path)

    net_value = _relpath(net_file)
    route_value = _relpath(route_file)
    fcd_value = os.path.basename(fcd_file)

    with open(cfg_path, 'w', encoding='utf-8') as f:
        f.write(f"""<configuration>
    <input>
        <net-file value="{net_value}"/>
        <route-files value="{route_value}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="{steps}"/>
    </time>
    <output>
        <fcd-output value="{fcd_value}"/>
    </output>
    <processing>
        <time-to-teleport value="300"/>
    </processing>
    <report>
        <no-step-log value="true"/>
    </report>
</configuration>""")


def _compare_results(baseline_fcd: str, optimized_fcd: str) -> str:
    """Compare baseline and optimized FCD results."""

    try:
        baseline_stats = _extract_fcd_stats(baseline_fcd)
        optimized_stats = _extract_fcd_stats(optimized_fcd)

        if not baseline_stats or not optimized_stats:
            return "Could not extract statistics for comparison."

        lines = ["\n" + "="*70]
        lines.append("PERFORMANCE COMPARISON")
        lines.append("="*70)

        # Average speed comparison
        baseline_speed = baseline_stats.get('avg_speed', 0)
        optimized_speed = optimized_stats.get('avg_speed', 0)
        speed_improvement = ((optimized_speed - baseline_speed) / baseline_speed * 100) if baseline_speed > 0 else 0

        lines.append(f"\nAverage Speed:")
        lines.append(f"  Baseline:  {baseline_speed:.2f} m/s")
        lines.append(f"  Optimized: {optimized_speed:.2f} m/s")
        lines.append(f"  Change:    {speed_improvement:+.2f}%")

        # Travel time comparison (inverse of speed, roughly)
        if speed_improvement > 0:
            lines.append(f"\n[+] Traffic flow improved by signal optimization")
        elif speed_improvement < -5:
            lines.append(f"\n[-] Traffic flow degraded (may need further tuning)")
        else:
            lines.append(f"\n[~] Minimal change in traffic flow")

        # Vehicle count
        baseline_vehicles = baseline_stats.get('vehicle_count', 0)
        optimized_vehicles = optimized_stats.get('vehicle_count', 0)

        lines.append(f"\nVehicle Count:")
        lines.append(f"  Baseline:  {baseline_vehicles}")
        lines.append(f"  Optimized: {optimized_vehicles}")

        lines.append("\n" + "="*70)

        return "\n".join(lines)

    except Exception as e:
        return f"Error comparing results: {e}"


def _extract_fcd_stats(fcd_file: str) -> dict:
    """Extract basic statistics from FCD output."""

    try:
        import xml.etree.ElementTree as ET

        tree = ET.parse(fcd_file)
        root = tree.getroot()

        speeds = []
        vehicles = set()

        for timestep in root.findall('timestep'):
            for vehicle in timestep.findall('vehicle'):
                vehicle_id = vehicle.get('id')
                speed = vehicle.get('speed')

                if vehicle_id:
                    vehicles.add(vehicle_id)
                if speed:
                    try:
                        speeds.append(float(speed))
                    except ValueError:
                        pass

        avg_speed = sum(speeds) / len(speeds) if speeds else 0

        return {
            'avg_speed': avg_speed,
            'vehicle_count': len(vehicles),
            'data_points': len(speeds)
        }

    except Exception as e:
        print(f"Warning: Could not extract FCD stats: {e}")
        return {}


if __name__ == "__main__":
    sys.exit(main())
