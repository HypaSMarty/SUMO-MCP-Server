import subprocess
import os
import sys
from typing import Optional, List

def tls_cycle_adaptation(net_file: str, route_files: str, output_file: str) -> str:
    """
    Wrapper for tlsCycleAdaptation.py. Adapts traffic light cycles based on traffic demand.
    """
    if 'SUMO_HOME' not in os.environ:
        return "Error: SUMO_HOME not set"
    
    script = os.path.join(os.environ['SUMO_HOME'], 'tools', 'tlsCycleAdaptation.py')
    if not os.path.exists(script):
        return f"Error: script not found at {script}"
        
    cmd = [sys.executable, script, "-n", net_file, "-r", route_files, "-o", output_file]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"tlsCycleAdaptation successful.\nStdout: {result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"tlsCycleAdaptation failed.\nStderr: {e.stderr}\nStdout: {e.stdout}"
    except Exception as e:
        return f"Error: {str(e)}"

def tls_coordinator(net_file: str, route_files: str, output_file: str, options: Optional[List[str]] = None) -> str:
    """
    Wrapper for tlsCoordinator.py. Optimizes traffic light coordination.
    
    Args:
        net_file: Path to network file.
        route_files: Path to route file(s).
        output_file: Path to output network file with coordinated signals.
    """
    if 'SUMO_HOME' not in os.environ:
        return "Error: SUMO_HOME not set"
    
    script = os.path.join(os.environ['SUMO_HOME'], 'tools', 'tlsCoordinator.py')
    if not os.path.exists(script):
        return f"Error: script not found at {script}"
        
    cmd = [sys.executable, script, "-n", net_file, "-r", route_files, "-o", output_file]
    
    if options:
        cmd.extend(options)
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"tlsCoordinator successful.\nStdout: {result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"tlsCoordinator failed.\nStderr: {e.stderr}\nStdout: {e.stdout}"
    except Exception as e:
        return f"tlsCoordinator execution error: {str(e)}"
