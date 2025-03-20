import requests
from bs4 import BeautifulSoup
import json
from mcp.server.fastmcp import FastMCP
from mcp.types import ErrorData, INTERNAL_ERROR
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

mcp = FastMCP("rotten_tomatoes")

def scrape_movie_details(movie_url):
    """
    Scrapes details from a specific movie page on Rotten Tomatoes.

    Args:
        movie_url (str): The URL of the movie page.

    Returns:
        dict: A dictionary containing movie details, or None if an error occurs.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(movie_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching movie details from {movie_url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    movie_details = {}

    try:
        # Extract description from meta tag
        description_element = soup.find('meta', {'name': 'description'})
        movie_details['description'] = description_element['content'].strip() if description_element and 'content' in description_element.attrs else "N/A"

        # Extract genre, rating, actors, and directors from ld+json
        ld_json_script = soup.find('script', {'type': 'application/ld+json'})
        if ld_json_script:
            ld_json = json.loads(ld_json_script.string)

            movie_details['genre'] = ld_json.get('genre', "N/A")
            movie_details['contentRating'] = ld_json.get('contentRating', "N/A")
            movie_details['actor'] = [actor['name'] for actor in ld_json.get('actor', [])]
            movie_details['director'] = [director['name'] for director in ld_json.get('director', [])]
        else:
            movie_details['genre'] = "N/A"
            movie_details['contentRating'] = "N/A"
            movie_details['actor'] = []
            movie_details['director'] = []

    except Exception as e:
        logging.error(f"Error extracting movie details: {e}")
        return None

    return movie_details

@mcp.tool()
def get_rotten_tomatoes_movies():
    """
    Scrapes movie information from Rotten Tomatoes.

    Returns:
        list: A list of dictionaries, where each dictionary contains movie information.
    """
    url = "https://www.rottentomatoes.com/browse/movies_at_home/sort:popular"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL: {e}")
        raise ValueError(f"Error fetching URL: {e}")

    soup = BeautifulSoup(response.content, 'html.parser')
    movie_list = []

    try:
        movie_containers = soup.select('div.discovery-tiles')
        if not movie_containers:
            logging.error("Could not find movie containers.")
            return None

        for container in movie_containers:
            movies = container.select('div.flex-container')
            if not movies:
                logging.warning("Could not find movies within container.")
                continue

            for movie in movies:
                title_element = movie.select_one('span.p--small')
                title = title_element.text.strip() if title_element else "N/A"

                score_pairs_element = movie.select_one('score-pairs-deprecated')

                if score_pairs_element:
                    critic_score_element = score_pairs_element.select_one('rt-text[slot="criticsScore"]')
                    audience_score_element = score_pairs_element.select_one('rt-text[slot="audienceScore"]')

                    critic_score = critic_score_element.text.strip() if critic_score_element else "N/A"
                    audience_score = audience_score_element.text.strip() if audience_score_element else "N/A"
                else:
                    critic_score = "N/A"
                    audience_score = "N/A"
                    
                streaming_date_element = movie.select_one('span.smaller')
                streaming_date = streaming_date_element.text.strip() if streaming_date_element else "N/A"

                # Extract the movie URL
                movie_url_element = movie.select_one('a[data-track="scores"]')
                movie_url = "https://www.rottentomatoes.com" + movie_url_element['href'] if movie_url_element and movie_url_element.has_attr('href') else "N/A"

                movie_info = {
                    'Film Title': title,
                    'Critic Rating': critic_score,
                    'Audience Rating': audience_score,
                    'Streaming Date': streaming_date,
                    'Movie URL': movie_url,
                }

                # Scrape additional details from the movie details page
                if movie_url != "N/A":
                    movie_details = scrape_movie_details(movie_url)
                    if movie_details:
                        movie_info.update({
                            'genre': movie_details.get('genre', "N/A"),
                            'contentRating': movie_details.get('contentRating', "N/A"),
                            'actor': movie_details.get('actor', []),
                            'director': movie_details.get('director', []),
                            'description': movie_details.get('description', "N/A")
                        })
                    else:
                        logging.warning(f"Could not retrieve details for {title} from {movie_url}")
                else:
                    logging.warning(f"Movie URL not available for {title}")

                movie_list.append(movie_info)
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        raise ValueError(f"Error during scraping: {e}")

    return movie_list
