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
            return self.client.networks.create(
                network_name, driver=self.NETWORK_DRIVER_TYPE
            )
        except Exception as e:
            logging.error(f"Failed to create network {network_name}: {e}")
            raise

    def remove_network(self, network: Network):
        try:
            network.remove()
        except Exception as e:
            logging.error(f"Failed to remove network {network.id}: {e}")

    def run_container(
        self, name: str, network_name: str, network: Network, host_name: str = None
    ) -> Container:
        try:
            command = "/bin/sh -c 'while true; do sleep 1; done'"
            container = self.client.containers.run(
                image="alpine:latest",
                name=name,
                hostname=host_name or name,
                detach=True,
                network=network_name,
                command=command,
            )
            logging.info(f"Started running container {container.id}")
            return container
        except Exception as e:
            logging.error(f"Failed to run container {name}: {e}")
            return None

    def remove_all_containers_from_network(self, network_id: str):
        network = self.client.networks.get(network_id=network_id)
        for container in network.containers:
            container.stop()
            self.remove_container(container=container)
        logging.info(f"All containers removed from {network.id}")

    def network_has_no_active_endpoints(self, network: Network) -> bool:
        try:
            return bool(not network.attrs["Containers"])
        except APIError as e:
            logging.error(
                f"Error checking active endpoints for network {network.id}: {e}"
            )
            return False

    def wait_for_no_active_endpoints(
        self, network: Network, timeout: int = 30, interval=2
    ):
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.network_has_no_active_endpoints(network=network):
                return True
            logging.info("Waiting for network to clear active endpoints...")
            time.sleep(interval)
        logging.error(
            f"Timeout waiting for network {network.id} to have no active endpoints"
        )
        return False

    def safely_remove_network(self, network_id: str):
        network = self.client.networks.get(network_id=network_id)
        if self.wait_for_no_active_endpoints(network=network):
            self.remove_network(network=network)
        else:
            logging.error(
                f"Network {network.id} could not be removed due to active endpoints or it timed out while trying to check for active endpoints"
            )

    def remove_container(self, container: Container):
        try:
            container.remove(force=True)
            logging.info(f"Successfully removed container: {container.id}")
        except APIError as e:
            logging.error(f"Failed to remove container {container.id}: {e}")

    def test_ping(self, from_container: Container, target_name: str) -> bool:
        container = self.client.containers.get(from_container.id)
        try:
            if container.status != "running":
                logging.error(f"Container {from_container.id} is not running.")
                return False
            result = container.exec_run(f"ping -c 3 {target_name}")
            success = "0% packet loss" in result.output.decode()
            logging.info(
                f"Ping from {container.name} to {target_name} {'succeeded' if success else 'failed'}"
            )
            return success
        except APIError as e:
            logging.error(f"Failed to ping from {container.id} to {target_name}: {e}")
            raise
