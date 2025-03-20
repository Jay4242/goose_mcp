import os
import requests
from mcp.server.fastmcp import FastMCP
from mcp.types import ErrorData, INTERNAL_ERROR
from mcp.shared.exceptions import McpError
import xmltodict

PLEX_URL = os.environ.get("PLEX_URL")
if not PLEX_URL:
    raise ValueError("PLEX_URL environment variable must be set.")
PLEX_LIBRARY_SECTION = os.environ.get("PLEX_LIBRARY_SECTION", "1")  # Movies
PLEX_TOKEN = os.environ.get("PLEX_API_KEY")

if not PLEX_TOKEN:
    raise ValueError("PLEX_API_KEY environment variable must be set.")

mcp = FastMCP("plex")

def _fetch_from_plex(endpoint):
    """Helper function to fetch data from Plex."""
    url = f"{PLEX_URL}{endpoint}?X-Plex-Token={PLEX_TOKEN}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return xmltodict.parse(response.text)
    except requests.exceptions.RequestException as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Error fetching from Plex: {e}"))

@mcp.tool()
def get_unwatched_movies() -> str:
    """
    Fetches a list of unwatched movies from your Plex library.

    Returns:
        A string containing a list of unwatched movie titles.
    """
    try:
        data = _fetch_from_plex(f"/library/sections/{PLEX_LIBRARY_SECTION}/unwatched")
        movies = data['MediaContainer']['Video']
        if isinstance(movies, list):
            movie_list = "\n".join([movie['@title'] for movie in movies])
        else:
            movie_list = movies['@title']  # Handle single movie case
        return movie_list
    except KeyError:
        raise McpError(ErrorData(INTERNAL_ERROR, "Unexpected data format from Plex."))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"An unexpected error occurred: {e}"))
