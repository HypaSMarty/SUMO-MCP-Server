import traci
import logging
from typing import Optional

from utils.sumo import find_sumo_binary

logger = logging.getLogger(__name__)

class SUMOConnection:
    """
    Singleton class to manage the connection to the SUMO server via TraCI.
    """
    _instance: Optional['SUMOConnection'] = None
    _connected: bool
    
    def __new__(cls) -> "SUMOConnection":
        if cls._instance is None:
            cls._instance = super(SUMOConnection, cls).__new__(cls)
            cls._instance._connected = False
        return cls._instance

    def connect(
        self,
        config_file: Optional[str] = None,
        gui: bool = False,
        port: int = 8813,
        host: str = "localhost",
    ) -> None:
        """
        Start SUMO and connect, or connect to an existing instance.
        If config_file is provided, starts a new instance.
        If config_file is None, attempts to connect to existing server at host:port.
        """
        if self._connected:
            logger.info("Already connected to SUMO.")
            return

        try:
            if config_file:
                binary_name = "sumo-gui" if gui else "sumo"
                binary = find_sumo_binary(binary_name)
                if not binary:
                    raise RuntimeError(
                        "Could not locate SUMO executable. "
                        "Please ensure SUMO is installed and either the binary is in PATH or SUMO_HOME is set."
                    )
                # Add --no-step-log to prevent stdout pollution which breaks JSON-RPC
                cmd = [binary, "-c", config_file, "--no-step-log", "true"]
                logger.info(f"Starting SUMO with command: {cmd}")
                traci.start(cmd, port=port) # Note: traci.start usually handles port selection or defaults
            else:
                logger.info(f"Connecting to existing SUMO at {host}:{port}")
                traci.init(host=host, port=port)
            
            self._connected = True
            logger.info("Successfully connected to SUMO.")
        except Exception as e:
            logger.error(f"Failed to connect to SUMO: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from SUMO server."""
        if not self._connected:
            return
        
        try:
            traci.close()
            logger.info("Disconnected from SUMO.")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        finally:
            self._connected = False

    def is_connected(self) -> bool:
        return self._connected
    
    def simulation_step(self, step: float = 0) -> None:
        """Advance the simulation."""
        if not self._connected:
             raise RuntimeError("Not connected to SUMO.")
        traci.simulationStep(step)

# Global instance
connection_manager = SUMOConnection()
