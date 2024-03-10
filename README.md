# Docker Network Provisioning Tool

## Brief

This project implements an initial version of a Python tool designed for programmatically provisioning Docker containers on virtual networks. It automates the setup, interaction, and teardown of Docker containers connected within a custom network.

## Functional Requirements

The tool fulfills the following core functionalities:

- **Container Provisioning**: Automatically runs two or more Docker containers. The containers are named and hosted as follows:
  - One container acts as the `attacker`.
  - Additional containers are designated as `target-0`, `target-1`, `target-2`, etc., depending on the specified context.

- **Network Creation**: Dynamically creates a Docker network named `hack-net` and connects all aforementioned containers to this network, enabling isolated communication.

- **Connectivity Testing**: Performs ping tests from the `attacker` container to each `target` container to ensure proper network connectivity and zero packet loss.

- **Cleanup**: Ensures a clean environment by removing all provisioned containers and the network after testing or upon user request.

## Getting Started

### Prerequisites

- Docker installed on your machine.
- Python 3.6 or higher.

## Usage

This Python tool automates the provisioning of Docker containers within a custom network. Here's how to get started:

### Basic Usage

To run the tool and provision your Docker environment, use the following command structure:

```bash
python path/to/src/CLI.py --targets <number_of_targets>
```
<number_of_targets> has to be greater than 0

## Output
The application will not generate any specific output, but for the logs showcasing the steps.