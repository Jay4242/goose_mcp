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
- List your shipping addresses
- Get a specific shipping address by ID
- Create a new shipping address
- Delete a shipping address by ID
- List your credit cards
- Get a specific credit card by ID
- Attach a credit card (tokenized via Stripe)
- Create a temporary URL for collecting credit card information
- Delete a credit card by ID
- Get your cart
- Add an item to your cart
- Set the shipping address for your cart
- Set the credit card for your cart
- Convert your cart to an order
- Clear your cart
- List your orders
- Get a specific order by ID
- Create a new order
- List your subscriptions
- Get a specific subscription by ID
- Update a subscription by ID
- Create a new subscription
- Delete a subscription by ID

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
-   `list_addresses`: Lists the current user's shipping addresses.
-   `get_address`: Gets a shipping address by ID.
-   `create_address`: Creates a new shipping address.
-   `delete_address`: Deletes a shipping address by ID.
-   `list_cards`: Lists the current user's credit cards.
-   `get_card`: Gets a credit card by ID.
-   `create_card`: Attaches a credit card (tokenized via Stripe) to the current user.
-   `collect_card`: Creates a temporary URL for collecting credit card information.
-   `delete_card`: Deletes a credit card by ID.
-   `get_cart`: Gets the current user's cart.
-   `set_cart_item`: Adds an item to the current user's cart.
-   `set_cart_address`: Sets the shipping address for the current user's cart.
-   `set_cart_card`: Sets the credit card for the current user's cart.
-   `convert_cart`: Converts the current user's cart to an order.
-   `clear_cart`: Clears the current user's cart.
-   `list_orders`: Lists the current user's orders.
-   `get_order`: Gets an order by ID.
-   `create_order`: Creates a new order.
-   `list_subscriptions`: Lists the current user's subscriptions.
-   `get_subscription`: Gets a subscription by ID.
-   `update_subscription`: Updates a subscription by ID.
-   `create_subscription`: Creates a new subscription.
-   `delete_subscription`: Deletes a subscription by ID.

## Using with Goose

To add this MCP server as an extension in Goose:

1.  Go to Settings > Extensions > Add.
2.  Set the Type to StandardIO.
3.  Provide the ID, name, and description for your extension.
4.  In the Command field, provide the path to your executable. For example:

    ```bash
    uv run /full/path/to/mcp-terminal-shop/.venv/bin/mcp_terminal_shop
    ```
