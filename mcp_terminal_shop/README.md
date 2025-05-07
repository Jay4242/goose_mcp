# Terminal Shop MCP Server

This is an MCP server that provides access to the Terminal API, allowing you to interact with the Terminal e-commerce platform through the Model Context Protocol.

## Overview

This server exposes several tools that allow you to:

- List products
- Get a specific product by ID
- List your personal access tokens
- Get a specific personal access token by ID
- Create a new personal access token
- Delete a personal access token by ID
- Get your user profile
- Update your user profile

## Getting Started

1.  **Set the `TERMINAL_BEARER_TOKEN` environment variable:** This is required to authenticate with the Terminal API. You can manage your personal access tokens in the Account page of the SSH shop:

    ```
    ssh dev.terminal.shop -t apps  # dev sandbox
    ssh terminal.shop -t apps      # production
    ```

2.  **Install the server:**

    ```bash
    uv pip install .
    ```

3.  **Run the server:**

    ```bash
    mcp_terminal_shop
    ```

## Configuration

The server uses the following environment variables:

-   `TERMINAL_BEARER_TOKEN`: Your personal access token for the Terminal API.
-   `API_URL`: (Optional) The base URL for the Terminal API. Defaults to `https://api.terminal.shop`.

## Tools

The following tools are available through this MCP server:

-   `list_products`: Lists all products for sale in the Terminal shop.
-   `get_product`: Gets a product by ID from the Terminal shop.
-   `list_tokens`: Lists the current user's personal access tokens.
-   `get_token`: Gets a personal access token by ID.
-   `create_token`: Creates a new personal access token.
-   `delete_token`: Deletes a personal access token by ID.
-   `get_profile`: Gets the current user's profile.
-   `update_profile`: Updates the current user's profile.

## Using with Goose

To add this MCP server as an extension in Goose:

1.  Go to Settings > Extensions > Add.
2.  Set the Type to StandardIO.
3.  Provide the ID, name, and description for your extension.
4.  In the Command field, provide the path to your executable. For example:

    ```bash
    uv run /full/path/to/mcp-terminal-shop/.venv/bin/mcp_terminal_shop
    ```
