import requests
from mcp.server.fastmcp import FastMCP
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import logging
import json

load_dotenv()

mcp = FastMCP("terminal_shop")

class Terminal:
    def __init__(self, api_url="https://api.terminal.shop", bearer_token=None):
        self.api_url = api_url
        self.bearer_token = bearer_token or os.getenv("TERMINAL_BEARER_TOKEN")
        if not self.bearer_token:
            raise ValueError("Bearer token is required.  Please set TERMINAL_BEARER_TOKEN environment variable or pass it to the Terminal constructor.")
        self.token = self.Token(self)
        self.profile = self.Profile(self)
        self.address = self.Address(self)
        self.card = self.Card(self)
        self.cart = self.Cart(self)
        self.order = self.Order(self)
        self.subscription = self.Subscription(self)

    def _get(self, path: str) -> Dict:
        return self._request("GET", path)

    def _put(self, path: str, data: Dict) -> Dict:
        return self._request("PUT", path, json=data)

    def _post(self, path: str, data: Dict) -> Dict:
        return self._request("POST", path, json=data)

    def _delete(self, path: str) -> Dict:
        return self._request("DELETE", path)

    def _request(self, method: str, path: str, json: Optional[Dict] = None) -> Dict:
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        try:
            response = requests.request(method, f"{self.api_url}{path}", headers=headers, json=json)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                raise ErrorData(INVALID_PARAMS, f"Bad Request: {e}")
            if response.status_code == 401:
                raise ErrorData(INTERNAL_ERROR, "Unauthorized: Invalid bearer token.") from e
            elif response.status_code == 404:
                raise ErrorData(INTERNAL_ERROR, "Not Found: Resource not found.") from e
            elif response.status_code == 429:
                raise ErrorData(INTERNAL_ERROR, "Too Many Requests: Rate limit exceeded.") from e
            else:
                raise ErrorData(INTERNAL_ERROR, f"API request failed with status code {response.status_code}: {e}") from e
        except requests.exceptions.RequestException as e:
            raise ErrorData(INTERNAL_ERROR, f"API request failed: {e}") from e

    def list_products(self) -> List[Dict]:
        """Lists all products for sale in the Terminal shop."""
        return self._get("/product")

    def get_product(self, product_id: str) -> Dict:
        """Gets a product by ID from the Terminal shop."""
        return self._get(f"/product/{product_id}")

    class Token:
        def __init__(self, terminal):
            self.terminal = terminal

        def list(self) -> List[Dict]:
            """Lists the current user's personal access tokens."""
            return self.terminal._get("/token")

        def get(self, token_id: str) -> Dict:
            """Gets a personal access token by ID."""
            return self.terminal._get(f"/token/{token_id}")

        def create(self) -> Dict:
            """Creates a new personal access token."""
            return self.terminal._post("/token")

        def delete(self, token_id: str) -> Dict:
            """Deletes a personal access token by ID."""
            return self.terminal._delete(f"/token/{token_id}")

    class Profile:
        def __init__(self, terminal):
            self.terminal = terminal

        def get(self) -> Dict:
            """Gets the current user's profile."""
            return self.terminal._get("/profile")

        def update(self, email: str = None, name: str = None) -> Dict:
            """Updates the current user's profile."""
            data = {}
            if email:
                data["email"] = email
            if name:
                data["name"] = name
            return self.terminal._put("/profile", data)

    class Address:
        def __init__(self, terminal):
            self.terminal = terminal

        def list(self) -> List[Dict]:
            """Lists the current user's shipping addresses."""
            return self.terminal._get("/address")

        def get(self, address_id: str) -> Dict:
            """Gets a shipping address by ID."""
            return self.terminal._get(f"/address/{address_id}")

        def create(self, city: str, country: str, name: str, street1: str, zip: str) -> Dict:
            """Creates a new shipping address."""
            data = {
                "city": city,
                "country": country,
                "name": name,
                "street1": street1,
                "zip": zip,
            }
            return self.terminal._post("/address", data)

        def delete(self, address_id: str) -> Dict:
            """Deletes a shipping address by ID."""
            return self.terminal._delete(f"/address/{address_id}")

    class Card:
        def __init__(self, terminal):
            self.terminal = terminal

        def list(self) -> List[Dict]:
            """Lists the current user's credit cards."""
            return self.terminal._get("/card")

        def get(self, card_id: str) -> Dict:
            """Gets a credit card by ID."""
            return self.terminal._get(f"/card/{card_id}")

        def create(self, token: str) -> Dict:
            """Attaches a credit card (tokenized via Stripe) to the current user."""
            data = {"token": token}
            return self.terminal._post("/card", data)

        def collect(self) -> Dict:
            """Creates a temporary URL for collecting credit card information."""
            return self.terminal._post("/card/collect")

        def delete(self, card_id: str) -> Dict:
            """Deletes a credit card by ID."""
            return self.terminal._delete(f"/card/{card_id}")

    class Cart:
        def __init__(self, terminal):
            self.terminal = terminal

        def get(self) -> Dict:
            """Gets the current user's cart."""
            return self.terminal._get("/cart")

        def set_item(self, product_variant_id: str, quantity: int) -> Dict:
            """Adds an item to the current user's cart."""
            data = {"product_variant_id": product_variant_id, "quantity": quantity}
            return self.terminal._put("/cart/item", data)

        def set_address(self, address_id: str) -> Dict:
            """Sets the shipping address for the current user's cart."""
            data = {"address_id": address_id}
            return self.terminal._put("/cart/address", data)

        def set_card(self, card_id: str) -> Dict:
            """Sets the credit card for the current user's cart."""
            data = {"card_id": card_id}
            return self.terminal._put("/cart/card", data)

        def convert(self) -> Dict:
            """Converts the current user's cart to an order."""
            return self.terminal._post("/cart/convert")

        def clear(self) -> Dict:
            """Clears the current user's cart."""
            return self.terminal._delete("/cart")

    class Order:
        def __init__(self, terminal):
            self.terminal = terminal

        def list(self) -> List[Dict]:
            """Lists the current user's orders."""
            return self.terminal._get("/order")

        def get(self, order_id: str) -> Dict:
            """Gets an order by ID."""
            return self.terminal._get(f"/order/{order_id}")

        def create(self, address_id: str, card_id: str, variants: Dict[str, int]) -> Dict:
            """Creates a new order."""
            data = {
                "address_id": address_id,
                "card_id": card_id,
                "variants": variants,
            }
            return self.terminal._post("/order", data)

    class Subscription:
        def __init__(self, terminal):
            self.terminal = terminal

        def list(self) -> List[Dict]:
            """Lists the current user's subscriptions."""
            return self.terminal._get("/subscription")

        def get(self, subscription_id: str) -> Dict:
            """Gets a subscription by ID."""
            return self.terminal._get(f"/subscription/{subscription_id}")

        def update(self, subscription_id: str, data: Dict) -> Dict:
            """Updates a subscription by ID."""
            return self.terminal._put(f"/subscription/{subscription_id}", data)

        def create(self, address_id: str, card_id: str, product_variant_id: str, quantity: int) -> Dict:
            """Creates a new subscription."""
            data = {
                "address_id": address_id,
                "card_id": card_id,
                "product_variant_id": product_variant_id,
                "quantity": quantity,
            }
            return self.terminal._post("/subscription", data)

        def delete(self, subscription_id: str) -> Dict:
            """Deletes a subscription by ID."""
            return self.terminal._delete(f"/subscription/{subscription_id}")


terminal_client: Optional[Terminal] = None

if os.getenv("TERMINAL_BEARER_TOKEN"):
    terminal_client = Terminal()
else:
    logging.warning("TERMINAL_BEARER_TOKEN is not set. Terminal shop tools will be disabled.")

def check_terminal_client():
    if terminal_client is None:
        raise ErrorData(INTERNAL_ERROR, "Terminal shop tools are disabled because TERMINAL_BEARER_TOKEN is not set.")

@mcp.tool()
def list_products() -> List[Dict]:
    """
    Lists all products for sale in the Terminal shop.
    """
    check_terminal_client()
    try:
        return terminal_client.list_products()
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to list products: {e}")

@mcp.tool()
def get_product(product_id: str) -> Dict:
    """
    Gets a product by ID from the Terminal shop.
    Args:
        product_id: ID of the product to get.
    """
    check_terminal_client()
    try:
        return terminal_client.get_product(product_id)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to get product: {e}")

@mcp.tool()
def list_tokens() -> List[Dict]:
    """Lists the current user's personal access tokens."""
    check_terminal_client()
    try:
        return terminal_client.token.list()
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to list tokens: {e}")

@mcp.tool()
def get_token(token_id: str) -> Dict:
    """Gets a personal access token by ID."""
    check_terminal_client()
    try:
        return terminal_client.token.get(token_id)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to get token: {e}")

@mcp.tool()
def create_token() -> Dict:
    """Creates a new personal access token."""
    check_terminal_client()
    try:
        return terminal_client.token.create()
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to create token: {e}")

@mcp.tool()
def delete_token(token_id: str) -> Dict:
    """Deletes a personal access token by ID."""
    check_terminal_client()
    try:
        return terminal_client.token.delete(token_id)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to delete token: {e}")

@mcp.tool()
def get_profile() -> Dict:
    """Gets the current user's profile."""
    check_terminal_client()
    try:
        return terminal_client.profile.get()
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to get profile: {e}")

@mcp.tool()
def update_profile(email: str = None, name: str = None) -> Dict:
    """Updates the current user's profile."""
    check_terminal_client()
    try:
        return terminal_client.profile.update(email=email, name=name)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to update profile: {e}")

@mcp.tool()
def list_addresses() -> List[Dict]:
    """Lists the current user's shipping addresses."""
    check_terminal_client()
    try:
        return terminal_client.address.list()
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to list addresses: {e}")

@mcp.tool()
def get_address(address_id: str) -> Dict:
    """Gets a shipping address by ID."""
    check_terminal_client()
    try:
        return terminal_client.address.get(address_id)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to get address: {e}")

@mcp.tool()
def create_address(city: str, country: str, name: str, street1: str, zip: str) -> Dict:
    """Creates a new shipping address."""
    check_terminal_client()
    try:
        return terminal_client.address.create(city, country, name, street1, zip)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to create address: {e}")

@mcp.tool()
def delete_address(address_id: str) -> Dict:
    """Deletes a shipping address by ID."""
    check_terminal_client()
    try:
        return terminal_client.address.delete(address_id)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to delete address: {e}")

@mcp.tool()
def list_cards() -> List[Dict]:
    """Lists the current user's credit cards."""
    check_terminal_client()
    try:
        return terminal_client.card.list()
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to list cards: {e}")

@mcp.tool()
def get_card(card_id: str) -> Dict:
    """Gets a credit card by ID."""
    check_terminal_client()
    try:
        return terminal_client.card.get(card_id)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to get card: {e}")

@mcp.tool()
def create_card(token: str) -> Dict:
    """Attaches a credit card (tokenized via Stripe) to the current user."""
    check_terminal_client()
    try:
        return terminal_client.card.create(token)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to create card: {e}")

@mcp.tool()
def collect_card() -> Dict:
    """Creates a temporary URL for collecting credit card information."""
    check_terminal_client()
    try:
        return terminal_client.card.collect()
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to collect card: {e}")

@mcp.tool()
def delete_card(card_id: str) -> Dict:
    """Deletes a credit card by ID."""
    check_terminal_client()
    try:
        return terminal_client.card.delete(card_id)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to delete card: {e}")

@mcp.tool()
def get_cart() -> Dict:
    """Gets the current user's cart."""
    check_terminal_client()
    try:
        return terminal_client.cart.get()
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to get cart: {e}")

@mcp.tool()
def set_cart_item(product_variant_id: str, quantity: int) -> Dict:
    """Adds an item to the current user's cart."""
    check_terminal_client()
    try:
        return terminal_client.cart.set_item(product_variant_id, quantity)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to set cart item: {e}")

@mcp.tool()
def set_cart_address(address_id: str) -> Dict:
    """Sets the shipping address for the current user's cart."""
    check_terminal_client()
    try:
        return terminal_client.cart.set_address(address_id)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to set cart address: {e}")

@mcp.tool()
def set_cart_card(card_id: str) -> Dict:
    """Sets the credit card for the current user's cart."""
    check_terminal_client()
    try:
        return terminal_client.cart.set_card(card_id)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to set cart card: {e}")

@mcp.tool()
def convert_cart() -> Dict:
    """Converts the current user's cart to an order."""
    check_terminal_client()
    try:
        return terminal_client.cart.convert()
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to convert cart: {e}")

@mcp.tool()
def clear_cart() -> Dict:
    """Clears the current user's cart."""
    check_terminal_client()
    try:
        return terminal_client.cart.clear()
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to clear cart: {e}")

@mcp.tool()
def list_orders() -> List[Dict]:
    """Lists the current user's orders."""
    check_terminal_client()
    try:
        return terminal_client.order.list()
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to list orders: {e}")

@mcp.tool()
def get_order(order_id: str) -> Dict:
    """Gets an order by ID."""
    check_terminal_client()
    try:
        return terminal_client.order.get(order_id)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to get order: {e}")

@mcp.tool()
def create_order(address_id: str, card_id: str, variants: Dict[str, int]) -> Dict:
    """Creates a new order."""
    check_terminal_client()
    try:
        return terminal_client.order.create(address_id, card_id, variants)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to create order: {e}")

@mcp.tool()
def list_subscriptions() -> List[Dict]:
    """Lists the current user's subscriptions."""
    check_terminal_client()
    try:
        return terminal_client.subscription.list()
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to list subscriptions: {e}")

@mcp.tool()
def get_subscription(subscription_id: str) -> Dict:
    """Gets a subscription by ID."""
    check_terminal_client()
    try:
        return terminal_client.subscription.get(subscription_id)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to get subscription: {e}")

@mcp.tool()
def update_subscription(subscription_id: str, data: str) -> Dict:
    """Updates a subscription by ID."""
    check_terminal_client()
    try:
        data_dict = json.loads(data)
        return terminal_client.subscription.update(subscription_id, data_dict)
    except json.JSONDecodeError as e:
        raise ErrorData(INVALID_PARAMS, f"Invalid JSON format: {e}")
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to update subscription: {e}")

@mcp.tool()
def create_subscription(address_id: str, card_id: str, product_variant_id: str, quantity: int) -> Dict:
    """Creates a new subscription."""
    check_terminal_client()
    try:
        return terminal_client.subscription.create(address_id, card_id, product_variant_id, quantity)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to create subscription: {e}")

@mcp.tool()
def delete_subscription(subscription_id: str) -> Dict:
    """Deletes a subscription by ID."""
    check_terminal_client()
    try:
        return terminal_client.subscription.delete(subscription_id)
    except Exception as e:
        raise ErrorData(INTERNAL_ERROR, f"Failed to delete subscription: {e}")
