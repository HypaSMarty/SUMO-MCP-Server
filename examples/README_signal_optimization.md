# Traffic Signal Optimization Scenario

This example demonstrates a complete workflow for traffic signal optimization using SUMO-MCP tools.

## Scenario Overview

The scenario performs the following steps:

1. **Generate Grid Network** - Creates a 4x4 grid network with automatic traffic light placement
2. **Generate Traffic Demand** - Creates random trips with realistic traffic patterns
3. **Compute Routes** - Calculates vehicle routes using SUMO's routing algorithm
4. **Baseline Simulation** - Runs simulation with original traffic light timings
5. **Optimize Signals** - Adapts traffic light cycle times based on traffic demand
6. **Optimized Simulation** - Runs simulation with optimized traffic light timings
7. **Compare Results** - Analyzes and compares performance metrics

## Requirements

- SUMO installed and accessible
- `SUMO_HOME` environment variable set (for Python tool scripts)
- Python 3.10+
- sumo-mcp package installed

## Running the Scenario

### Basic Usage

```bash
python examples/signal_optimization_scenario.py
```

### With Explicit SUMO_HOME

```bash
export SUMO_HOME=/path/to/sumo  # Linux/macOS
# or
set SUMO_HOME=C:\Program Files\Eclipse\sumo  # Windows

python examples/signal_optimization_scenario.py
```

## Output

The script creates a timestamped output directory under `examples/` with the following files:

```
examples/signal_optimization_YYYYMMDD_HHMMSS/
├── grid.net.xml           # Network file with traffic lights
├── trips.xml              # Generated trip definitions
├── routes.xml             # Computed vehicle routes
├── baseline.sumocfg       # Baseline simulation config
├── baseline_fcd.xml       # Baseline floating car data
├── optimized.net.xml      # TLS programs (SUMO <additional> file), not a full .net.xml
├── optimized.sumocfg      # Optimized simulation config
└── optimized_fcd.xml      # Optimized floating car data
```

## Expected Results

The scenario typically shows:

- **Traffic Light Count**: ~9-12 traffic lights in a 4x4 grid
- **Vehicle Count**: ~900 vehicles over 30 minutes
- **Baseline Performance**: Initial traffic flow metrics
- **Optimized Performance**: Improved average speeds (5-15% typical improvement)

## Customization

You can modify the scenario parameters at the top of the script:

```python
GRID_SIZE = 4              # Network size (NxN grid)
SIMULATION_STEPS = 1800    # Simulation duration (seconds)
TRAFFIC_PERIOD = 2.0       # Average time between vehicles (seconds)
```

## Visualization

To visualize the results:

```bash
cd examples/signal_optimization_YYYYMMDD_HHMMSS/

# View baseline simulation
sumo-gui -c baseline.sumocfg

# View optimized simulation
sumo-gui -c optimized.sumocfg
```

## Analysis

The script automatically compares:

- Average vehicle speeds (baseline vs. optimized)
- Total vehicle count
- Traffic flow efficiency

For detailed analysis, you can:

1. Use SUMO's built-in analysis tools
2. Process the FCD (Floating Car Data) XML files
3. Use third-party visualization tools

## Troubleshooting

### "Could not locate SUMO tool script"

Ensure `SUMO_HOME` is set and points to your SUMO installation directory:

```bash
echo $SUMO_HOME  # Should show /path/to/sumo
ls $SUMO_HOME/tools/randomTrips.py  # Should exist
```

### "Network generation failed"

Check that SUMO binaries are in your PATH:

```bash
sumo --version  # Should show SUMO version
netgenerate --version  # Should show version
```

### Poor optimization results

The traffic light optimization depends on:

- Traffic demand patterns (try adjusting `TRAFFIC_PERIOD`)
- Network topology (try different `GRID_SIZE`)
- Simulation duration (try longer `SIMULATION_STEPS`)

## Advanced Usage

### Custom Network Configuration

Modify the `netgenerate` options to create different network types:

```python
result = netgenerate(
    net_file,
    grid=True,
    grid_number=GRID_SIZE,
    options=[
        "--default.lanenumber", "3",      # More lanes
        "--default.speed", "16.67",       # 60 km/h
        "--tls.cycle.time", "90",         # Longer cycle time
        "--tls.green.time", "45",         # Longer green phase
    ]
)
```

### Different Traffic Patterns

Generate rush-hour traffic with higher demand:

```python
result = random_trips(
    net_file,
    trips_file,
    end_time=SIMULATION_STEPS,
    period=1.0,  # More frequent vehicles
    options=[
        "--fringe-factor", "10",  # Heavy edge traffic
        "--insertion-density", "5"  # More aggressive insertion
    ]
)
```

### Alternative Optimization Methods

Try the traffic light coordinator instead of cycle adaptation:

```python
from mcp_tools.signal import tls_coordinator

result = tls_coordinator(net_file, routes_file, optimized_net)
```

## References

- [SUMO Traffic Light Documentation](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html)
- [SUMO Network Generation](https://sumo.dlr.de/docs/Networks/PlainXML.html)
- [SUMO Demand Modeling](https://sumo.dlr.de/docs/Demand/Introduction.html)
- [SUMO-MCP Documentation](../README.md)

## License

This example is part of the SUMO-MCP project and follows the same license.
