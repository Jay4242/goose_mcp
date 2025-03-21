# mcp_doctl

## Description

`mcp_doctl` is an MCP (Model Context Protocol) server that allows you to manage DigitalOcean resources using the `doctl` command-line tool. It provides a set of tools that can be called to perform various actions on your DigitalOcean account, such as creating, listing, and deleting droplets, as well as executing commands on them.

## Tools

The following tools are available:

*   **create\_droplet**: Creates a new DigitalOcean droplet.
*   **list\_droplets**: Lists all DigitalOcean droplets in your account.
*   **delete\_droplet**: Deletes a DigitalOcean droplet.
*   **execute\_command\_on\_droplet**: Executes a command on a DigitalOcean droplet.
*   **list\_available\_images**: Lists available images for creating droplets.
*   **list\_available\_regions**: Lists available regions for creating droplets.
*   **list\_available\_sizes**: Lists available sizes for creating droplets.
*   **check\_droplet\_responsiveness**: Checks if a droplet is responsive.
*   **oneclick\_list\_images**: Lists available 1-click images.

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

1.  Run the `mcp_doctl` server:

    ```bash
    mcp_doctl
    ```

2.  Connect to the server using an MCP client.

## Configuration

The `mcp_doctl` server uses the `doctl` command-line tool, so you need to configure `doctl` with your DigitalOcean API token. See the [doctl documentation](https://www.digitalocean.com/docs/cli/how-to/configure/) for more information.

