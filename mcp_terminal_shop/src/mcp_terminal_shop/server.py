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

    def _get(self, path: str) -> Dict:
        return self._request("GET", path)

    def _put(self, path: str, data: Dict) -> Dict:
        return self._request("PUT", path, json=data)

    def _post(self, path: str) -> Dict:
        return self._request("POST", path)

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
