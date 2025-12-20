import os
import shutil
from typing import Optional, List
from mcp_tools.simulation import run_simple_simulation
from mcp_tools.signal import tls_cycle_adaptation, tls_coordinator
from mcp_tools.analysis import analyze_fcd

def signal_opt_workflow(
    net_file: str, 
    route_file: str, 
    output_dir: str, 
    steps: int = 3600,
    use_coordinator: bool = False
) -> str:
    """
    Signal Optimization Workflow.
    1. Run Baseline Simulation
    2. Optimize Signals (Cycle Adaptation or Coordinator)
    3. Run Optimized Simulation
    4. Compare Results
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Baseline paths
    baseline_cfg = os.path.join(output_dir, "baseline.sumocfg")
    baseline_fcd = os.path.join(output_dir, "baseline_fcd.xml")
    
    # Optimized paths
    opt_net_file = os.path.join(output_dir, "optimized.net.xml")
    opt_cfg = os.path.join(output_dir, "optimized.sumocfg")
    opt_fcd = os.path.join(output_dir, "optimized_fcd.xml")
    
    # 1. Run Baseline
    _create_config(baseline_cfg, net_file, route_file, baseline_fcd, steps)
    res_baseline = run_simple_simulation(baseline_cfg, steps)
    if "error" in res_baseline.lower():
        return f"Baseline Simulation Failed: {res_baseline}"
        
    analysis_baseline = analyze_fcd(baseline_fcd)
    
    # 2. Optimize
    if use_coordinator:
        res_opt = tls_coordinator(net_file, route_file, opt_net_file)
    else:
        res_opt = tls_cycle_adaptation(net_file, route_file, opt_net_file)
        
    if "failed" in res_opt.lower() or "error" in res_opt.lower():
        return f"Optimization Failed: {res_opt}"
    
    # Check if optimized file is valid and determines if it is a net or additional
    is_additional = _is_additional_file(opt_net_file)
    
    # 3. Run Optimized
    if is_additional:
        # Use original net + additional file
        _create_config(opt_cfg, net_file, route_file, opt_fcd, steps, additional_files=[opt_net_file])
    else:
        # Use new net file
        _create_config(opt_cfg, opt_net_file, route_file, opt_fcd, steps)
        
    res_optimized = run_simple_simulation(opt_cfg, steps)
    if "error" in res_optimized.lower():
        return f"Optimized Simulation Failed: {res_optimized}"
        
    analysis_optimized = analyze_fcd(opt_fcd)
    
    return (f"Signal Optimization Workflow Completed.\n\n"
            f"--- Baseline Results ---\n{res_baseline}\n{analysis_baseline}\n\n"
            f"--- Optimization Step ---\n{res_opt}\n\n"
            f"--- Optimized Results ---\n{res_optimized}\n{analysis_optimized}")

def _is_additional_file(file_path: str) -> bool:
    if not os.path.exists(file_path): return False
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            head = f.read(1000)
        return '<additional' in head
    except:
        return False

def _create_config(cfg_path: str, net_file: str, route_file: str, fcd_file: str, steps: int, additional_files: Optional[List[str]] = None) -> None:
    additional_str = ""
    if additional_files:
        val = ",".join([os.path.abspath(f) for f in additional_files])
        additional_str = f'<additional-files value="{val}"/>'
        
    with open(cfg_path, "w") as f:
        f.write(f"""<configuration>
    <input>
        <net-file value="{os.path.abspath(net_file)}"/>
        <route-files value="{os.path.abspath(route_file)}"/>
        {additional_str}
    </input>
    <time>
        <begin value="0"/>
        <end value="{steps}"/>
    </time>
    <output>
        <fcd-output value="{os.path.abspath(fcd_file)}"/>
    </output>
</configuration>""")
