import os
import sys
import gymnasium as gym
from sumo_rl import SumoEnvironment
from typing import List, Optional, Dict, Any

def list_rl_scenarios() -> List[str]:
    """
    List available built-in RL scenarios from sumo-rl package.
    These are typically folders in sumo_rl/nets.
    """
    try:
        import sumo_rl
        base_path = os.path.dirname(sumo_rl.__file__)
        nets_path = os.path.join(base_path, 'nets')
        if not os.path.exists(nets_path):
            return ["Error: sumo-rl nets directory not found"]
        
        scenarios = [d for d in os.listdir(nets_path) if os.path.isdir(os.path.join(nets_path, d))]
        return sorted(scenarios)
    except Exception as e:
        return [f"Error listing scenarios: {str(e)}"]

def create_rl_environment(
    net_file: str,
    route_file: str,
    out_csv_name: Optional[str] = None,
    use_gui: bool = False,
    num_seconds: int = 100000,
    reward_fn: str = 'diff-waiting-time'
) -> str:
    """
    Validate and prepare an RL environment configuration.
    Actual environment creation happens in the training process due to Gym's nature.
    This tool validates inputs and returns a configuration summary.
    """
    if not os.path.exists(net_file):
        return f"Error: Network file not found at {net_file}"
    if not os.path.exists(route_file):
        return f"Error: Route file not found at {route_file}"
        
    return (f"RL Environment Configuration Valid:\n"
            f"- Net: {net_file}\n"
            f"- Route: {route_file}\n"
            f"- Reward Function: {reward_fn}\n"
            f"- GUI: {use_gui}\n"
            f"- Horizon: {num_seconds} steps")

def run_rl_training(
    net_file: str,
    route_file: str,
    out_dir: str,
    episodes: int = 1,
    steps_per_episode: int = 1000,
    algorithm: str = "ql",
    reward_type: str = "diff-waiting-time"
) -> str:
    """
    Run a basic RL training session using Q-Learning (default) or other algorithms.
    This runs synchronously and returns the result.
    """
    try:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            
        env = SumoEnvironment(
            net_file=net_file,
            route_file=route_file,
            out_csv_name=os.path.join(out_dir, "train_results"),
            use_gui=False,
            num_seconds=steps_per_episode,
            reward_fn=reward_type
        )
        
        # Simple Q-Learning implementation for demonstration
        # In a real scenario, this would be more complex or use Stable Baselines3
        if algorithm == "ql":
            from sumo_rl.agents import QLAgent
            
            initial_states, _ = env.reset()
            agents = {
                ts: QLAgent(
                    starting_state=env.encode(initial_states[ts], ts),
                    state_space=env.observation_space,
                    action_space=env.action_space,
                    alpha=0.1,
                    gamma=0.99,
                    exploration_strategy='EpsilonGreedy'
                ) for ts in env.ts_ids
            }
            
            info_log = []
            
            for ep in range(1, episodes + 1):
                obs, _ = env.reset()
                done = {agent_id: False for agent_id in env.ts_ids}
                total_reward = 0
                
                while not all(done.values()):
                    actions = {ts: agents[ts].act() for ts in env.ts_ids}
                    next_obs, rewards, done, truncated, _ = env.step(actions)
                    
                    for ts in env.ts_ids:
                        agents[ts].learn(
                            next_state=env.encode(next_obs[ts], ts),
                            reward=rewards[ts]
                        )
                        total_reward += rewards[ts]
                        
                    obs = next_obs
                
                env.save_csv(out_dir, ep)
                info_log.append(f"Episode {ep}/{episodes}: Total Reward = {total_reward}")
                env.close()
                
            return "\n".join(info_log)
        
        else:
            return f"Algorithm {algorithm} not yet implemented in this tool wrapper."
            
    except Exception as e:
        return f"Training failed: {str(e)}"
