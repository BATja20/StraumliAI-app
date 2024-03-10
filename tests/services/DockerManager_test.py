from unittest.mock import patch, Mock, ANY
import pytest
from docker.models.networks import Network
from pytest_mock import mocker
from src.services.DockerManager import DockerManager
from docker.errors import APIError


@pytest.fixture
def docker_manager():
    manager = DockerManager()
    yield manager


@patch("docker.models.networks.NetworkCollection.create")
def test_create_network_success(mock_create, docker_manager):
    mock_network = Mock()
    mock_network.name = "mock_network"

    mock_create.return_value = mock_network

    result = docker_manager.create_network("test_network")
    assert result.name == "mock_network"
    mock_create.assert_called_once_with("test_network", driver="bridge")


@patch("logging.error")
@patch(
    "docker.models.networks.NetworkCollection.create",
    side_effect=Exception("Creation failed"),
)
def test_create_network_failure_logs_error(mock_run, mock_logging, docker_manager):
    with pytest.raises(Exception):
        docker_manager.create_network("test_network")
    mock_logging.assert_called()


def test_remove_network_success(mocker, docker_manager):
    mock_network = Mock(spec=Network)
    mocker.patch.object(mock_network, "remove")

    docker_manager.remove_network(mock_network)
    mock_network.remove.assert_called_once()


@patch("logging.error")
def test_remove_network_failure_logs_error(mock_logging, mocker, docker_manager):
    mock_network = Mock(spec=Network)
    mocker.patch.object(mock_network, "remove", side_effect=APIError("Removal failed"))

    docker_manager.remove_network(mock_network)
    mock_logging.assert_called_with(mocker.ANY)


@patch(
    "docker.models.networks.NetworkCollection.create",
    side_effect=Exception("Test error"),
)
def test_create_network_failure(mocker, docker_manager):

    with pytest.raises(Exception) as e:
        docker_manager.create_network("test_network")
    assert "Test error" in str(e)


def test_remove_network(mocker, docker_manager):
    mock_network = mocker.Mock(spec=Network)
    mock_remove = mocker.patch.object(mock_network, "remove")

    docker_manager.remove_network(mock_network)
    mock_remove.assert_called_once()


@patch("docker.models.containers.ContainerCollection.run")
def test_run_container_success(mock_run, docker_manager):
    mock_container = Mock(id="mock_id")
    mock_run.return_value = mock_container

    result = docker_manager.run_container(
        "test_container", "test_network", Mock(spec=Network)
    )
    assert result.id == "mock_id"
    mock_run.assert_called_with(
        image="alpine:latest",
        name="test_container",
        hostname=ANY,
        detach=True,
        network="test_network",
        command=ANY,
    )


@patch("logging.error")
@patch(
    "docker.models.containers.ContainerCollection.run",
    side_effect=Exception("Run failed"),
)
def test_run_container_failure_logs_error(mock_run, mock_logging, docker_manager):

    result = docker_manager.run_container(
        "container_name", "network_name", Mock(spec=Network)
    )
    assert result is None
    mock_logging.assert_called_with(ANY)
