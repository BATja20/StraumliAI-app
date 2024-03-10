import pytest
from docker.models.networks import Network
from src.services.DockerManager import DockerManager
from docker.errors import APIError

@pytest.fixture
def docker_manager():
    manager = DockerManager()
    yield manager

def test_create_network_success(mocker, docker_manager):
    mock_network = mocker.Mock()
    mock_network.name = "mock_network"

    mock_create = mocker.patch("docker.models.networks.NetworkCollection.create")
    mock_create.return_value = mock_network

    result = docker_manager.create_network("test_network")
    assert result.name == "mock_network"
    mock_create.assert_called_once_with("test_network", driver="bridge")

def test_create_network_failure_logs_error(mocker, docker_manager):
    mocker.patch('docker.models.networks.NetworkCollection.create', side_effect=Exception("Creation failed"))
    mock_logging = mocker.patch('logging.error')

    with pytest.raises(Exception):
        docker_manager.create_network("test_network")
    mock_logging.assert_called()

def test_remove_network_success(mocker, docker_manager):
    mock_network = mocker.Mock(spec=Network)
    mocker.patch.object(mock_network, 'remove')

    docker_manager.remove_network(mock_network)
    mock_network.remove.assert_called_once()
    
def test_remove_network_failure_logs_error(mocker, docker_manager):
    mock_network = mocker.Mock(spec=Network)
    mocker.patch.object(mock_network, 'remove', side_effect=APIError("Removal failed"))
    mock_logging = mocker.patch('logging.error')

    docker_manager.remove_network(mock_network)
    mock_logging.assert_called_with(mocker.ANY) 

def test_create_network_failure(mocker, docker_manager):
    mocker.patch(
        "docker.models.networks.NetworkCollection.create",
        side_effect=Exception("Test error"),
    )

    with pytest.raises(Exception) as e:
        docker_manager.create_network("test_network")
    assert "Test error" in str(e)


def test_remove_network(mocker, docker_manager):
    mock_network = mocker.Mock(spec=Network)
    mock_remove = mocker.patch.object(mock_network, "remove")

    docker_manager.remove_network(mock_network)
    mock_remove.assert_called_once()


def test_run_container_success(mocker, docker_manager):
    mock_run = mocker.patch("docker.models.containers.ContainerCollection.run")
    mock_container = mocker.Mock(id="mock_id")
    mock_run.return_value = mock_container

    result = docker_manager.run_container(
        "test_container", "test_network", mocker.Mock(spec=Network)
    )
    assert result.id == "mock_id"
    mock_run.assert_called_with(image="alpine:latest", name="test_container", hostname=mocker.ANY, detach=True, network="test_network", command=mocker.ANY)
    
def test_run_container_failure_logs_error(mocker, docker_manager):
    mocker.patch('docker.models.containers.ContainerCollection.run', side_effect=Exception("Run failed"))
    mock_logging = mocker.patch('logging.error')

    result = docker_manager.run_container("container_name", "network_name", mocker.Mock(spec=Network))
    assert result is None
    mock_logging.assert_called_with(mocker.ANY) 

