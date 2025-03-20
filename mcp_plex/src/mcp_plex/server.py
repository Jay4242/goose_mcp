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
    Fetches a list of unwatched movies from your Plex library with details.

    Returns:
        A string containing a list of unwatched movie titles, ratings, year, and summary.
    """
    try:
        data = _fetch_from_plex(f"/library/sections/{PLEX_LIBRARY_SECTION}/unwatched")
        movies = data['MediaContainer']['Video']
        if isinstance(movies, list):
            movie_list = ""
            for movie in movies:
                title = movie['@title']
                rating = movie.get('@rating', 'N/A')
                audience_rating = movie.get('@audienceRating', 'N/A')
                year = movie.get('@year', 'N/A')
                summary = movie.get('@summary', 'N/A')
                directors = ", ".join([d['@tag'] for d in movie.get('Director', [])]) if isinstance(movie.get('Director'), list) else movie.get('Director', 'N/A')
                genres = ", ".join([g['@tag'] for g in movie.get('Genre', [])]) if isinstance(movie.get('Genre'), list) else movie.get('Genre', 'N/A')

                movie_list += f"Title: {title}\n"
                movie_list += f"Rating: {rating}\n"
                movie_list += f"Audience Rating: {audience_rating}\n"
                movie_list += f"Year: {year}\n"
                movie_list += f"Summary: {summary}\n"
                movie_list += f"Director(s): {directors}\n"
                movie_list += f"Genre(s): {genres}\n\n"
            return movie_list
        else:
            # Handle single movie case
            title = movies['@title']
            rating = movies.get('@rating', 'N/A')
            audience_rating = movies.get('@audienceRating', 'N/A')
            year = movies.get('@year', 'N/A')
            summary = movies.get('@summary', 'N/A')
            directors = ", ".join([d['@tag'] for d in movies.get('Director', [])]) if isinstance(movies.get('Director'), list) else movies.get('Director', 'N/A')
            genres = ", ".join([g['@tag'] for g in movies.get('Genre', [])]) if isinstance(movies.get('Genre'), list) else movies.get('Genre', 'N/A')

            movie_list = f"Title: {title}\n"
            movie_list += f"Rating: {rating}\n"
            movie_list += f"Audience Rating: {audience_rating}\n"
            movie_list += f"Year: {year}\n"
            movie_list += f"Summary: {summary}\n"
            movie_list += f"Director(s): {directors}\n"
            movie_list += f"Genre(s): {genres}\n"
            return movie_list
    except KeyError:
        raise McpError(ErrorData(INTERNAL_ERROR, "Unexpected data format from Plex."))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"An unexpected error occurred: {e}"))
