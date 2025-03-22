import os
import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from typing import List, Dict
import html2text
from pdfminer.high_level import extract_text
import io

mcp = FastMCP("searxng")

SEARXNG_BASE_URL = os.environ.get("SEARXNG_BASE_URL")
if not SEARXNG_BASE_URL:
    raise ValueError("SEARXNG_BASE_URL environment variable must be set.")

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"


@mcp.tool()
def searxng_search(query: str, max_results: int = 30) -> List[Dict[str, str]]:
    """
    Searches the web using a SearxNG instance and returns a list of results.

    Args:
        query: The search query.
        max_results: The maximum number of results to return. Defaults to 30.

    Returns:
        A list of dictionaries, where each dictionary represents a search result
        and contains the title, URL, and content snippet.  Returns an error
        message in a dictionary if the search fails.
    """
    if max_results <= 0:
        raise McpError(ErrorData(INVALID_PARAMS, "max_results must be greater than 0."))

    search_url = f"{SEARXNG_BASE_URL}/search"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': USER_AGENT
    }
    data = f"q={query}&categories=general&language=auto&time_range=&safesearch=0&theme=simple"

    try:
        response = requests.post(search_url, headers=headers, data=data, verify=False, timeout=30)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        for article in soup.find_all('article', class_='result')[:max_results]:
            url_header = article.find('a', class_='url_header')
            if url_header:
                url = url_header['href']
                title = article.find('h3').text.strip() if article.find('h3') else "No Title"
                description = article.find('p', class_='content').text.strip() if article.find('p', class_='content') else "No Description"
                results.append({
                    'title': title,
                    'url': url,
                    'content': description
                })
        return results
    except requests.exceptions.RequestException as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Error during search: {str(e)}"))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Unexpected error: {str(e)}"))


@mcp.tool()
def fetch_and_clean(url: str) -> str:
    """
    Fetches content from a URL, determines the content type (HTML or PDF),
    cleans the text, and returns the cleaned text.

    Args:
        url: The URL to fetch and clean.

    Returns:
        The cleaned text content of the URL.
    """
    try:
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '').lower()

        if 'application/pdf' in content_type:
            # Handle PDF content
            pdf_file = io.BytesIO(response.content)
            text = extract_text(pdf_file)
            return text
        else:
            # Handle HTML content (or default to HTML if content type is unknown)
            html_content = response.text
            text_maker = html2text.HTML2Text()
            text_maker.body_width = 0  # Disable line wrapping
            markdown_text = text_maker.handle(html_content)
            return markdown_text
    except requests.exceptions.RequestException as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Error fetching URL: {str(e)}"))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Unexpected error: {str(e)}"))
