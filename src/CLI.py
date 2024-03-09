import argparse
import logging
from services.DockerManager import DockerManager

class CLI:
    
    NETWORK_NAME = 'hack-net'
    
    def __init__(self):
        self.manager = DockerManager()
    
    @staticmethod
    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description='Manages Docker containers on a network')
        parser.add_argument('--targets', type=int, help = 'Number of target containers to create', required = True)
        return parser.parse_args()
    
    def run_pipeline(self, targets_count: int) -> bool:
        is_success = False
        try:
            network = self.manager.create_network(network_name = self.NETWORK_NAME)
            attacker = self.manager.run_container("attacker", network_name = self.NETWORK_NAME, network = network)
            
            targets = []
            for i in range(targets_count):
                try:
                    target_container = self.manager.run_container(f"target-{i}", self.NETWORK_NAME, network = network)
                    targets.append(target_container)
                except Exception as e:
                    logging.error(f"Failed to create target container: {e}")

            targets = [target for target in targets if target is not None]
            logging.info(f"targets: {targets}")
            
            is_success = all(self.manager.test_ping(attacker, target_name = target.attrs["Name"][1:]) for target in targets) # [1:] is to remove the leading slash
            logging.info(f"Ping Test Results: {'Successful' if is_success else 'Failed'}")
            return is_success
        except Exception as e:
            logging.error(f"Error encountered while running pipeline: {e}")
            return False
        finally:
            self.manager.remove_all_containers_from_network(network_id = network.id)
            self.manager.safely_remove_network(network_id = network.id)
            return is_success
            
            
    def run(self) -> None:
        args = self.parse_args()
        success = self.run_pipeline(targets_count = args.targets)
        exit(0 if success else 1)
    
if  __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    manager = DockerManager()
    cli = CLI()
    cli.run()