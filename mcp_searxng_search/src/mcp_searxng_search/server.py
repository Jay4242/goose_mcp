import os
import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from typing import List, Dict, Literal, Optional
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

    if not query:
        return [{'error': 'No Query Submitted'}]

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
        if not results:
            return [{"error": "No results found for the given query."}]
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


@mcp.tool()
def searxng_news_search(query: str, time_range: Optional[Literal["day", "week", "month", "year"]] = None, max_results: int = 30) -> List[Dict[str, str]]:
    """
    Searches the web for news articles using a SearxNG instance and returns a list of results.

    Args:
        query: The search query.
        time_range:  The time range to filter results by.  Valid values are "day", "week", "month", and "year". Defaults to no time limit.
        max_results: The maximum number of results to return. Defaults to 30.

    Returns:
        A list of dictionaries, where each dictionary represents a search result
        and contains the title, URL, and content snippet. Returns an error
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

    time_range_param = f"&time_range={time_range}" if time_range else ""
    data = f"q={query}&categories=news&language=auto{time_range_param}&safesearch=0&theme=simple"

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
        if not results:
            return [{"error": "No news articles found for the given query."}]
        return results
    except requests.exceptions.RequestException as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Error during search: {str(e)}"))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Unexpected error: {str(e)}"))


@mcp.tool()
def searxng_file_search(query: str, time_range: Optional[Literal["day", "week", "month", "year"]] = None, max_results: int = 30) -> List[Dict[str, str]]:
    """
    Searches for files using a SearxNG instance and returns a list of results, including magnet URIs,
    seeders, and leechers.

    Args:
        query: The search query.
        time_range: The time range to filter results by. Valid values are "day", "week", "month", and "year". Defaults to no time limit.
        max_results: The maximum number of results to return. Defaults to 30.

    Returns:
        A list of dictionaries, where each dictionary represents a search result
        and contains the title, URL, magnet URI, number of seeders, and number of leechers.
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

    time_range_param = f"&time_range={time_range}" if time_range else ""
    data = f"q={query}&categories=files&language=auto{time_range_param}&safesearch=0&theme=simple"

    try:
        response = requests.post(search_url, headers=headers, data=data, verify=False, timeout=30)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        for article in soup.find_all('article', class_='result', limit=max_results):
            result = {}
            url_header = article.find('a', class_='url_header')
            if url_header:
                result['url'] = url_header['href']
                result['title'] = article.find('h3').text.strip() if article.find('h3') else "No Title"

            altlink = article.find('p', class_='altlink')
            if altlink:
                magnet_link = altlink.find('a', href=lambda href: href and "magnet:" in href)
                if magnet_link:
                    result['magnet'] = magnet_link['href']

            stat_elements = article.find_all('p', class_='stat')
            seeders = "N/A"
            leechers = "N/A"
            if len(stat_elements) >= 1:
                seeder_element = stat_elements[0].find('span', class_='badge')
                if seeder_element:
                    seeders = seeder_element.text.replace("Seeder", "").strip()
            if len(stat_elements) >= 2:
                leech_element = stat_elements[1].find('span', class_='badge')
                if leech_element:
                    leechers = leech_element.text.replace("Leecher", "").strip()

            result['seeders'] = seeders
            result['leechers'] = leechers

            results.append(result)

        if not results:
            return [{"error": "No files found for the given query."}]
        return results
    except requests.exceptions.RequestException as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Error during search: {str(e)}"))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Unexpected error: {str(e)}"))
