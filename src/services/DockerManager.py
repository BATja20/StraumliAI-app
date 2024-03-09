import logging
import docker
import time
from docker.models.containers import Container
from docker.models.networks import Network
from docker.errors import APIError

class DockerManager:
    NETWORK_DRIVER_TYPE = "bridge"
    
    def __init__(self):
        self.client = docker.from_env()
        
    def create_network(self, network_name: str) -> Network:
        try:
            return self.client.networks.create(network_name, driver = self.NETWORK_DRIVER_TYPE)
        except Exception as e:
            logging.error(f"Failed to create network {network_name}: {e}")
            raise
    
    def remove_network(self, network: Network) -> None:
        try:
            network.remove()
        except Exception as e:
            logging.error(f"Failed to remove network {network.id}: {e}")
            raise
        
    def run_container(self, name: str, network_name: str, image: str = "alpine:latest", host_name: str = None) -> Container:
        try:
            self.client.containers.run(image = image, name = name, hostname = host_name or name, detach = True, network = network_name)
        except Exception as e:
            logging.error(f"Failed to run container {name}: {e}")
            raise
    
    def remove_all_containers_from_network(self, network: Network):
        for container in network.containers:
            container.stop()
            container.remove() 
            network.disconnect(container = container, force = True)
        logging.info(f"All containers removed from {network.id}")
        
    def network_has_no_active_endpoints(self, network: Network) -> bool:
        try:
            return bool(not network.attrs['Containers']) 
        except APIError as e:
               logging.error(f"Error checking active endpoints for network {network.id}: {e}")
               return False
           
    def wait_for_no_active_endpoints(self, network: Network, timeout: int = 30, interval = 2):
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.network_has_no_active_endpoints(network = network):
                logging.info(f"Network {network.id} has no active endpoints")
                return True
            logging.info("Waiting for network to clear active endpoints...")
            time.sleep(interval)
        logging.error(f"Timeout waiting for network {network.id} to have no active endpoints")
        return False
    
    def safely_remove_network(self, network: Network) -> None:
        time.sleep(1)
        if self.wait_for_no_active_endpoints(network = network):
            self.remove_network(network = network)
        else:
            logging.error(f"Network {network.id} could not be removed due to active endpoints or it timed out while trying to check for active endpoints")


                
    def remove_container(self, container: Container) -> None:
        if container is None:
            logging.warning("Attempted to remove a None container!!!")
            return
        container.remove(force = True)
        
    def test_ping(self, from_container: Container, target_name: str) -> bool:
        try:
            result = from_container.exec_run(f"ping -c 3 {target_name}")
            success = "0% packet loss" in result.output.decode()
            logging.info(f"Ping from {from_container.name} to {target_name} {'succeeded' if success else 'failed'}")
        except docker.errors.APIError as e:
            logging.error(f"Failed to ping from {from_container.name} to {target_name}: {e.explanation}")
            raise