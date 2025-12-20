import subprocess
import sumolib
import os
import sys
from typing import Optional, List

def netconvert(osm_file: str, output_file: str, options: Optional[List[str]] = None) -> str:
    """
    Wrapper for SUMO netconvert. Converts OSM files to SUMO network files.
    """
    try:
        binary = sumolib.checkBinary('netconvert')
    except Exception as e:
        return f"Error finding netconvert: {e}"

    cmd = [binary, "--osm-files", osm_file, "-o", output_file]
    if options:
        cmd.extend(options)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"Netconvert successful.\nStdout: {result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Netconvert failed.\nStderr: {e.stderr}\nStdout: {e.stdout}"
    except Exception as e:
        return f"Netconvert execution error: {str(e)}"

def netgenerate(output_file: str, grid: bool = True, grid_number: int = 3, options: Optional[List[str]] = None) -> str:
    """
    Wrapper for SUMO netgenerate. Generates abstract networks.
    """
    try:
        binary = sumolib.checkBinary('netgenerate')
    except Exception as e:
        return f"Error finding netgenerate: {e}"

    cmd = [binary, "-o", output_file]
    if grid:
        cmd.extend(["--grid", "--grid.number", str(grid_number)])
    
    if options:
        cmd.extend(options)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"Netgenerate successful.\nStdout: {result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Netgenerate failed.\nStderr: {e.stderr}\nStdout: {e.stdout}"
    except Exception as e:
        return f"Netgenerate execution error: {str(e)}"

def osm_get(bbox: str, output_dir: str, prefix: str = "osm", options: Optional[List[str]] = None) -> str:
    """
    Wrapper for osmGet.py. Downloads OSM data.
    
    Args:
        bbox: Bounding box "west,south,east,north".
        output_dir: Directory to save the data.
        prefix: Prefix for output files.
    """
    if 'SUMO_HOME' not in os.environ:
        return "Error: SUMO_HOME not set"
    
    script = os.path.join(os.environ['SUMO_HOME'], 'tools', 'osmGet.py')
    if not os.path.exists(script):
        return f"Error: osmGet.py not found at {script}"
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # osmGet.py writes to current dir or specified prefix. 
    # We should run it in the output_dir or handle paths carefully.
    # It seems osmGet.py uses --prefix to specify output filename prefix.
    
    cmd = [sys.executable, script, "--bbox", bbox, "--prefix", prefix]
    
    if options:
        cmd.extend(options)
        
    try:
        # Run in output_dir so files are saved there
        result = subprocess.run(cmd, cwd=output_dir, capture_output=True, text=True, check=True)
        return f"osmGet successful.\nStdout: {result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"osmGet failed.\nStderr: {e.stderr}\nStdout: {e.stdout}"
    except Exception as e:
        return f"osmGet execution error: {str(e)}"
