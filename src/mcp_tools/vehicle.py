import traci
from typing import List, Tuple
from utils.connection import connection_manager

def get_vehicles() -> List[str]:
    """Get the list of all active vehicle IDs."""
    if not connection_manager.is_connected():
        return []
    return list(traci.vehicle.getIDList())

def get_vehicle_speed(vehicle_id: str) -> float:
    """Get the speed of a specific vehicle (m/s)."""
    if not connection_manager.is_connected():
        raise RuntimeError("Not connected to SUMO.")
    return traci.vehicle.getSpeed(vehicle_id)

def get_vehicle_position(vehicle_id: str) -> Tuple[float, float]:
    """Get the (x, y) position of a specific vehicle."""
    if not connection_manager.is_connected():
        raise RuntimeError("Not connected to SUMO.")
    return traci.vehicle.getPosition(vehicle_id)

def get_vehicle_acceleration(vehicle_id: str) -> float:
    """Get the acceleration of a specific vehicle (m/s^2)."""
    if not connection_manager.is_connected():
        raise RuntimeError("Not connected to SUMO.")
    return traci.vehicle.getAcceleration(vehicle_id)

def get_vehicle_lane(vehicle_id: str) -> str:
    """Get the lane ID of a specific vehicle."""
    if not connection_manager.is_connected():
        raise RuntimeError("Not connected to SUMO.")
    return traci.vehicle.getLaneID(vehicle_id)

def get_vehicle_route(vehicle_id: str) -> List[str]:
    """Get the route (list of edge IDs) of a specific vehicle."""
    if not connection_manager.is_connected():
        raise RuntimeError("Not connected to SUMO.")
    return list(traci.vehicle.getRoute(vehicle_id))

def get_simulation_info() -> dict:
    """Get general simulation statistics."""
    if not connection_manager.is_connected():
        raise RuntimeError("Not connected to SUMO.")
    return {
        "time": traci.simulation.getTime(),
        "loaded_vehicles": traci.simulation.getLoadedNumber(),
        "departed_vehicles": traci.simulation.getDepartedNumber(),
        "arrived_vehicles": traci.simulation.getArrivedNumber(),
        "min_expected_vehicles": traci.simulation.getMinExpectedNumber()
    }
