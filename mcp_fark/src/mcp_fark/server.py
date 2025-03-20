import requests
from bs4 import BeautifulSoup
import argparse
import random
from mcp.server.fastmcp import FastMCP
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from requests.exceptions import RequestException

mcp = FastMCP("fark")

def _fetch_fark_headlines():
    url = "https://www.fark.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.content
    except RequestException as e:
        raise mcp.McpError(ErrorData(INTERNAL_ERROR, f"Failed to fetch Fark headlines: {e}"))

def _parse_fark_headlines(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    headlines = []
    headline_container = soup.find(id="headline_container")
    if headline_container:
        for td in headline_container.find_all("td", class_="headlineSourceImage"):
            a_tag = td.find("a", class_="outbound_link")
            if a_tag:
                url = a_tag["href"]
                # Find the parent table row
                parent_tr = td.find_parent("tr")
                # Find the headlineText td within the same row
                headline_text_td = parent_tr.find("td", class_="headlineText")
                if headline_text_td:
                    headline_span = headline_text_td.find("span", class_="headline")
                    if headline_span:
                        headline_a = headline_span.find("a", class_="outbound_link")
                        if headline_a:
                            tag = headline_a.text.strip()
                            if "photoshop" not in tag.lower() and "youtube" not in tag.lower():
                                headlines.append({"url": url, "tag": tag})
    return headlines

@mcp.tool()
def resolve_redirect_url(url: str) -> str:
    """
    Resolves a redirect URL to its final destination.

    Args:
        url (str): The URL to resolve.

    Returns:
        str: The resolved URL.

    Raises:
        McpError: If there's an error during the request.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        refresh_tag = soup.find("meta", attrs={"http-equiv": "refresh"})
        if refresh_tag:
            content = refresh_tag["content"]
            redirect_url = content.split("url=")[-1]
            return redirect_url
        else:
            a_tag = soup.find("a")
            if a_tag:
                redirect_url = a_tag["href"]
                return redirect_url
            else:
                return url  # If no meta refresh tag or a tag is found, return the original URL
    except requests.exceptions.RequestException as e:
        raise mcp.McpError(ErrorData(INTERNAL_ERROR, f"Error resolving URL {url}: {e}"))
        return url  # Return the original URL on error

@mcp.tool()
def get_fark_headlines(shuffle: bool = False, limit: int = 0) -> list[str]:
    """
    Fetches and parses headlines from Fark.com.

    Args:
        shuffle (bool, optional): Shuffles the headlines if True. Defaults to False.
        limit (int, optional): Limits the number of headlines returned. Defaults to 0 (no limit).

    Returns:
        list[str]: List of Fark.com headlines ("url | tag").
    """
    html_content = _fetch_fark_headlines()
    headlines = _parse_fark_headlines(html_content)

    # Shuffle the headlines if shuffle is True
    if shuffle:
        random.shuffle(headlines)

    headline_strings = [f"{headline['url']} | {headline['tag']}" for headline in headlines]

    # Limit the number of headlines if limit is greater than 0
    if limit > 0:
        headline_strings = headline_strings[:limit]

    return headline_strings
