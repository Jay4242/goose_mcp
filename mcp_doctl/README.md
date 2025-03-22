# mcp_doctl

## Description

`mcp_doctl` is an MCP (Model Context Protocol) server that allows you to manage DigitalOcean resources using the `doctl` command-line tool. It provides a set of tools that can be called to perform various actions on your DigitalOcean account, such as creating, listing, and deleting droplets, as well as executing commands on them.

## Tools

The following tools are available:

*   **create_droplet**: Creates a new DigitalOcean droplet with configurable region, size, and image.  If no name is provided, a name will be automatically generated. Requires the `DIGITALOCEAN_SSH_KEY_ID` environment variable to be set.
*   **list_droplets**: Lists all DigitalOcean droplets in your account.
*   **delete_droplet**: Deletes a DigitalOcean droplet by ID.
*   **execute_command_on_droplet**: Executes a command on a specified DigitalOcean droplet via SSH.
*   **list_available_images**: Lists available public images for creating droplets.
*   **list_available_regions**: Lists available regions for creating droplets.
*   **list_available_sizes**: Lists available sizes for creating droplets.
*   **check_droplet_responsiveness**: Checks if a droplet is responsive by attempting to connect via SSH.
*   **oneclick_list_images**: Lists available 1-click images.
*   **get_droplet_limit**: Retrieves the DigitalOcean account's droplet limit.
*   **resize_droplet**: Resizes a droplet to a specified size.
*   **reboot_droplet**: Reboots a droplet.
*   **shutdown_droplet**: Shuts down a droplet.
*   **rebuild_droplet**: Rebuilds a droplet with a specified image.

## Requirements

*   `doctl` command-line tool installed and configured with your DigitalOcean account.
*   Python 3.10 or higher.
*   `mcp` Python package.
*   `requests` Python package.

## Installation

1.  Install the required Python packages:

    ```bash
    pip install mcp[cli] requests
    ```

2.  Clone this repository:

    ```bash
    git clone <repository_url>
    cd mcp_doctl
    ```

3.  Install the `mcp_doctl` package:

    ```bash
    pip install .
    ```

## Usage

1.  Set the `DIGITALOCEAN_SSH_KEY_ID` environment variable to your DigitalOcean SSH key ID:

    ```bash
    export DIGITALOCEAN_SSH_KEY_ID=<your_ssh_key_id>
    ```

2.  You can synchronize the project dependencies and create a virtual environment using `uv`:

    ```bash
    uv sync
    ```

3.  Run the `mcp_doctl` server using `uv`:

    ```bash
    uv run /path/to/mcp_doctl/.venv/bin/mcp_doctl
    ```

4.  Connect to the server using an MCP client.

## Configuration

The `mcp_doctl` server uses the `doctl` command-line tool, so you need to configure `doctl` with your DigitalOcean API token. See the [doctl documentation](https://www.digitalocean.com/docs/cli/how-to/configure/) for more information.
