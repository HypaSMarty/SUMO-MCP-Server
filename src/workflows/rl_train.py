import os
from mcp_tools.rl import run_rl_training, list_rl_scenarios

def rl_train_workflow(
    scenario_name: str,
    output_dir: str,
    episodes: int = 5,
    steps: int = 1000
) -> str:
    """
    Workflow to train an RL agent on a built-in sumo-rl scenario.
    1. Locate scenario files
    2. Run training
    3. Return summary
    """
    import sumo_rl
    base_path = os.path.dirname(sumo_rl.__file__)
    scenario_path = os.path.join(base_path, 'nets', scenario_name)
    
    if not os.path.exists(scenario_path):
        available = list_rl_scenarios()
        return f"Error: Scenario '{scenario_name}' not found. Available: {available}"
    
    # Find .net.xml and .rou.xml in the scenario folder
    net_file = None
    route_file = None
    
    for f in os.listdir(scenario_path):
        if f.endswith(".net.xml"):
            net_file = os.path.join(scenario_path, f)
        elif f.endswith(".rou.xml"):
            route_file = os.path.join(scenario_path, f)
            
    if not net_file or not route_file:
        return f"Error: Could not find .net.xml or .rou.xml in {scenario_path}"
        
    return run_rl_training(
        net_file=net_file,
        route_file=route_file,
        out_dir=output_dir,
        episodes=episodes,
        steps_per_episode=steps,
        algorithm="ql"
    )
