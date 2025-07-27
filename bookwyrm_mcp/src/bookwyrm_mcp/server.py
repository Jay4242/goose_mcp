import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS

BASE_URL = "https://bookwyrm.social"

mcp = FastMCP("bookwyrm_mcp")

@mcp.tool()
def search_bookwyrm_books(query: str) -> list[dict]:
    """
    Searches bookwyrm.social for books matching the provided query.
    Returns a list of dictionaries, where each dictionary represents a book with fields:
    'title', 'key', 'author', 'year', 'cover', and 'confidence'.
    Usage:
        search_bookwyrm_books("The Lord of the Rings")
    """
    try:
        search_url = f"{BASE_URL}/search.json"
        params = {"q": query, "type": "book"}
        response = httpx.get(search_url, params=params, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except httpx.RequestError as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Network error while searching Bookwyrm: {str(e)}")) from e
    except httpx.HTTPStatusError as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Bookwyrm API returned an error: {e.response.status_code} - {e.response.text}")) from e
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Unexpected error during Bookwyrm search: {str(e)}")) from e

@mcp.tool()
def get_user_read_books_shelf_info(username: str) -> dict:
    """
    Retrieves information about a user's "read" books shelf from bookwyrm.social.
    Returns a dictionary representing the user's read shelf, including metadata and a list of books.
    Usage:
        get_user_read_books_shelf_info("username")
    """
    try:
        read_shelf_url = f"{BASE_URL}/user/{username}/shelf/read.json"
        headers = {"Accept": "application/activity+json"}
        response = httpx.get(read_shelf_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except httpx.RequestError as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Network error while fetching read books for {username}: {str(e)}")) from e
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise McpError(ErrorData(INVALID_PARAMS, f"User or read shelf not found for {username}")) from e
        raise McpError(ErrorData(INTERNAL_ERROR, f"Bookwyrm API returned an error for {username}: {e.response.status_code} - {e.response.text}")) from e
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Unexpected error during fetching read books for {username}: {str(e)}")) from e

@mcp.tool()
def get_user_reviews(username: str) -> list[dict]:
    """
    Retrieves a user's reviews from bookwyrm.social and parses the HTML content.
    Returns a list of dictionaries, where each dictionary represents a review with fields:
    'book_title', 'author', 'rating', and 'review_text'.
    Usage:
        get_user_reviews("username")
    """
    try:
        reviews_url = f"{BASE_URL}/user/{username}/reviews-comments"
        response = httpx.get(reviews_url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        reviews = []

        # Find all review articles
        review_articles = soup.find_all('article', class_='card')

        for article in review_articles:
            book_title = 'N/A'
            author = 'N/A'
            rating = 'N/A'
            review_text = ''

            # Extract info from header (for user who rated, book title, author, rating)
            header_h3 = article.find('header', class_='card-header')
            if header_h3:
                # The h3 tag in the header contains the user, book title, author, and rating summary
                title_author_rating_h3 = header_h3.find('h3')

                if title_author_rating_h3:
                    # Book Title
                    book_link = title_author_rating_h3.find('a', href=lambda h: h and '/book/' in h)
                    if book_link:
                        book_title = book_link.get_text(strip=True)

                    # Author - look for the specific author link with itemprop="name" or class "author"
                    author_link = title_author_rating_h3.find('a', class_='author')
                    if author_link:
                        author_span = author_link.find('span', itemprop='name')
                        author = author_span.get_text(strip=True) if author_span else author_link.get_text(strip=True)
                    
                    # Rating - look for the screen reader only text
                    rating_span = title_author_rating_h3.find('span', class_='is-sr-only')
                    if rating_span:
                        rating = rating_span.get_text(strip=True)

            # Extract review text from content section
            content_section = article.find('section', class_='card-content')
            if content_section:
                review_text_parts = []
                # Iterate through children of content_section to find text blocks that are not the initial book info div
                for child in content_section.children:
                    if child.name == 'div' and 'columns' in child.get('class', []):
                        # This is the book cover/details block, skip it.
                        continue
                    # Check if the child is a tag and has text content
                    if child.name in ['p', 'div'] and child.get_text(strip=True):
                        review_text_parts.append(child.get_text(strip=True))
                
                review_text = '\n'.join(review_text_parts).strip()
            
            reviews.append({
                'book_title': book_title,
                'author': author,
                'rating': rating,
                'review_text': review_text
            })
        return reviews
    except httpx.RequestError as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Network error while fetching reviews for {username}: {str(e)}")) from e
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise McpError(ErrorData(INVALID_PARAMS, f"User reviews not found for {username}")) from e
        raise McpError(ErrorData(INTERNAL_ERROR, f"Bookwyrm API returned an error for {username}: {e.response.status_code} - {e.response.text}")) from e
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Unexpected error during fetching and parsing reviews for {username}: {str(e)}")) from e

def get_user_read_books_html_info(html_content: str) -> list[dict]:
    """
    Parses the HTML content of a Bookwyrm user's "read" shelf and extracts book information.
    This function is intended for internal use and is not exposed as an MCP tool.
    Returns a list of dictionaries, where each dictionary represents a book with fields:
    'title' and 'author'.
    Usage:
        get_user_read_books_html_info("<html>...</html>")
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        books = []
        # Find the table containing book information
        book_table = soup.find('table', class_='table is-striped is-fullwidth is-mobile')
        if book_table:
            # Iterate over rows, skipping the header
            for row in book_table.find('tbody').find_all('tr', class_='book-preview'):
                title_tag = row.find('td', {'data-title': 'Title'})
                author_tag = row.find('td', {'data-title': 'Author'})

                title = title_tag.get_text(strip=True) if title_tag else 'N/A'
                author = author_tag.get_text(strip=True) if author_tag else 'N/A'
                
                books.append({'title': title, 'author': author})
        return books
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Error parsing HTML for read books: {str(e)}")) from e

@mcp.tool()
def get_user_read_books_from_url(username: str, page: int = 1) -> list[dict]:
    """
    Fetches the HTML content of a Bookwyrm user's "read" shelf and extracts book information.
    Returns a list of dictionaries, where each dictionary represents a book with fields:
    'title' and 'author'.
    Args:
        username (str): The username of the Bookwyrm user.
        page (int, optional): The page number of the read shelf to fetch. Defaults to 1.
    Usage:
        get_user_read_books_from_url("some_username", page=2)
    """
    try:
        read_shelf_url = f"{BASE_URL}/user/{username}/books/read?page={page}"
        response = httpx.get(read_shelf_url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return get_user_read_books_html_info(response.text)
    except httpx.RequestError as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Network error while fetching read books for {username}: {str(e)}")) from e
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise McpError(ErrorData(INVALID_PARAMS, f"User or read shelf not found for {username}")) from e
        raise McpError(ErrorData(INTERNAL_ERROR, f"Bookwyrm API returned an error for {username}: {e.response.status_code} - {e.response.text}")) from e
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Unexpected error during fetching and parsing read books for {username}: {str(e)}")) from e
