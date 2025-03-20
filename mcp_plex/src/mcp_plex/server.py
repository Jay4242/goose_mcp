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

def _format_movie_list(movies):
    """Helper function to format a list of movies into a string."""
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
        return _format_movie_list(movies)
    except KeyError:
        raise McpError(ErrorData(INTERNAL_ERROR, "Unexpected data format from Plex."))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"An unexpected error occurred: {e}"))

@mcp.tool()
def get_genres() -> str:
    """
    Fetches movie genres from Plex.

    Returns:
        A string containing a list of movie genres in the format "key: title".
    """
    try:
        data = _fetch_from_plex(f"/library/sections/{PLEX_LIBRARY_SECTION}/genre")
        genres = data['MediaContainer']['Directory']
        if isinstance(genres, list):
            genre_list = ""
            for genre in genres:
                genre_list += f"{genre['@key']}: {genre['@title']}\n"
            return genre_list
        else:
            return f"{genres['@key']}: {genres['@title']}"
    except KeyError:
        raise McpError(ErrorData(INTERNAL_ERROR, "Unexpected data format from Plex."))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"An unexpected error occurred: {e}"))

@mcp.tool()
def get_movies_by_genre(genre_id: int) -> str:
    """
    Fetches a list of movies for a specific genre from your Plex library.
    To ensure correct operation, you MUST validate the genre_id against the output of `get_genres`.

    Args:
        genre_id: The key/ID of the genre to search for.

    Returns:
        A string containing a list of movie titles, ratings, year, and summary for the specified genre.
    """
    try:
        data = _fetch_from_plex(f"/library/sections/{PLEX_LIBRARY_SECTION}/genre/{str(genre_id)}")
        movies = data['MediaContainer']['Video']
        return _format_movie_list(movies)
    except KeyError:
        raise McpError(ErrorData(INTERNAL_ERROR, "Unexpected data format from Plex."))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"An unexpected error occurred: {e}"))

@mcp.tool()
def get_all_movies() -> str:
    """
    Fetches all movies from your Plex library with details.

    Returns:
        A string containing a list of all movie titles, ratings, year, and summary.
    """
    try:
        data = _fetch_from_plex(f"/library/sections/{PLEX_LIBRARY_SECTION}/all")
        movies = data['MediaContainer']['Video']
        return _format_movie_list(movies)
    except KeyError:
        raise McpError(ErrorData(INTERNAL_ERROR, "Unexpected data format from Plex."))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"An unexpected error occurred: {e}"))
