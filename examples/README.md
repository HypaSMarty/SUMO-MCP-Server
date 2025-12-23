# Examples Directory

This directory contains example scenarios demonstrating SUMO-MCP capabilities.

## Available Examples

### 1. Traffic Signal Optimization Scenario

**File:** `signal_optimization_scenario.py`

**Description:** A complete end-to-end workflow demonstrating:
- Automated grid network generation with traffic lights
- Random traffic demand generation
- Baseline simulation with default signal timings
- Traffic signal optimization using demand-adaptive algorithms
- Performance comparison and analysis

**Key Features:**
- No manual network design required
- Automatic traffic light placement at major intersections
- Demand-based signal timing optimization
- Quantitative performance metrics

**Quick Start:**
```bash
# Ensure SUMO_HOME is set
export SUMO_HOME=/path/to/sumo  # or set on Windows

# Run the scenario
python examples/signal_optimization_scenario.py
```

**Expected Output:**
- Timestamped output directory with all simulation files
- Console output showing:
  - Network statistics (grid size, traffic light count)
  - Traffic demand (trip count)
  - Baseline performance (average speed, vehicle count)
  - Optimized performance
  - Performance improvement percentage

**Documentation:** See `README_signal_optimization.md` for detailed usage, customization options, and troubleshooting.

---

## Running Examples

### Prerequisites

1. **SUMO Installation**: Ensure SUMO is installed and accessible
2. **Environment Setup**: Set `SUMO_HOME` environment variable
3. **Python Environment**: Python 3.10+ with sumo-mcp installed

### General Pattern

All examples follow a similar pattern:

```bash
# Set SUMO environment
export SUMO_HOME=/path/to/sumo  # Linux/macOS
# or
set SUMO_HOME=C:\Program Files\Eclipse\sumo  # Windows

# Run example
python examples/<example_name>.py
```

### Output Structure

Each example creates a timestamped output directory:

```
examples/<scenario_name>_YYYYMMDD_HHMMSS/
├── *.net.xml      # Network files
├── *.rou.xml      # Route files
├── *.sumocfg      # SUMO configuration files
├── *_fcd.xml      # Floating car data (simulation output)
└── ...            # Additional scenario-specific files
```

---

## Example Categories

### Network Design Examples
- Grid network generation with traffic lights
- Custom intersection design
- Multi-modal network (vehicles + pedestrians)

### Traffic Demand Examples
- Random trip generation
- Origin-destination matrix conversion
- Time-varying demand patterns

### Simulation Examples
- Baseline simulation
- Multi-scenario comparison
- Parameter sensitivity analysis

### Optimization Examples
- **Traffic signal optimization** (implemented)
- Route optimization
- Traffic assignment

### Analysis Examples
- Floating car data analysis
- Travel time distribution
- Network performance metrics

---

## Contributing Examples

To add a new example:

1. Create a self-contained Python script in this directory
2. Follow the naming convention: `<scenario_name>_scenario.py`
3. Include a corresponding `README_<scenario_name>.md` with:
   - Scenario description
   - Usage instructions
   - Expected results
   - Customization options
4. Add entry to this `README.md`
5. Ensure the example uses ASCII characters only (no emoji)

### Example Template

```python
#!/usr/bin/env python3
"""
Brief scenario description.

This script demonstrates:
- Feature 1
- Feature 2
- Feature 3
"""

import os
import sys

# Add src to path for direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from mcp_tools import ...

def main() -> int:
    """Main scenario logic."""
    # Implementation
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'mcp_tools'`

**Solution**: Ensure you're running from the project root and src path is added:
```python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
```

**Issue**: `Could not locate SUMO tool script`

**Solution**: Set `SUMO_HOME` environment variable:
```bash
export SUMO_HOME=/usr/share/sumo  # Linux
export SUMO_HOME=/usr/local/share/sumo  # macOS Homebrew
set SUMO_HOME=C:\Program Files\Eclipse\sumo  # Windows
```

**Issue**: `Error finding sumo binary`

**Solution**: Add SUMO bin directory to PATH:
```bash
export PATH=$SUMO_HOME/bin:$PATH  # Linux/macOS
set PATH=%SUMO_HOME%\bin;%PATH%  # Windows
```

### Getting Help

- Check example-specific README files
- Review main project [README](../README.md)
- Check [SUMO documentation](https://sumo.dlr.de/docs/)
- Open an issue on GitHub

---

## Performance Notes

- **Small Networks** (4x4 grid): ~5-10 seconds total runtime
- **Medium Networks** (8x8 grid): ~30-60 seconds total runtime
- **Large Networks** (16x16 grid): ~5-10 minutes total runtime

Optimization runtime depends on:
- Network complexity (number of traffic lights)
- Traffic demand (number of vehicles)
- Simulation duration

---

## References

- [SUMO Documentation](https://sumo.dlr.de/docs/)
- [SUMO Tutorial](https://sumo.dlr.de/docs/Tutorials/index.html)
- [SUMO-MCP Project](https://github.com/your-org/sumo-mcp)

---

## License

All examples are part of the SUMO-MCP project and follow the project license.
