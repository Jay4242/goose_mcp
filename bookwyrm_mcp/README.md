# Bookwyrm MCP

This project provides a set of tools to interact with Bookwyrm, a federated social network for readers.

## Available Tools

### `search_bookwyrm_books(query: str)`
Searches bookwyrm.social for books matching the provided query.
Returns a list of dictionaries, where each dictionary represents a book with fields: 'title', 'key', 'author', 'year', 'cover', and 'confidence'.

**Usage:**
```python
search_bookwyrm_books("The Lord of the Rings")
```

### `get_user_read_books_shelf_info(username: str)`
Retrieves information about a user's "read" books shelf from bookwyrm.social.
Returns a dictionary representing the user's read shelf, including metadata and a list of books.

**Usage:**
```python
get_user_read_books_shelf_info("username")
```

### `get_user_reviews(username: str)`
Retrieves a user's reviews from bookwyrm.social and parses the HTML content.
Returns a list of dictionaries, where each dictionary represents a review with fields: 'book_title', 'author', 'rating', and 'review_text'.

**Usage:**
```python
get_user_reviews("username")
```

### `get_user_read_books_from_url(username: str, page: int = 1)`
Fetches the HTML content of a Bookwyrm user's "read" shelf and extracts book information.
Returns a list of dictionaries, where each dictionary represents a book with fields: 'title' and 'author'.

**Usage:**
```python
get_user_read_books_from_url("some_username", page=2)
```

## Integration with Goose

To add Bookwyrm MCP as an extension in Goose:

1.  Go to Settings > Extensions > Add.
2.  Set the Type to StandardIO.
3.  Provide an ID, name, and description for your extension (e.g., ID: `bookwyrm-mcp`, Name: `Bookwyrm MCP`, Description: `Tools for interacting with Bookwyrm`).
4.  In the Command field, provide the absolute path to your executable. For example:
    ```bash
    uv run /path/to/your/bookwyrm_mcp/.venv/bin/bookwyrm-mcp
    ```
    (Replace `/home/anon/test/aider/projects/goose/bookwyrm_mcp/` with the actual absolute path to your `bookwyrm_mcp` project directory if it's different.)

