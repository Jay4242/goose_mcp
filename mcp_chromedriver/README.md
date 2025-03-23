# MCP ChromeDriver

This is an [MCP](https://modelcontextprotocol.io/) server that allows [Goose](https://block.github.io/goose/) to interact with and control a Chrome browser instance using [ChromeDriver](https://chromedriver.chromium.org/). It provides a set of tools to automate web browsing tasks, such as navigating to URLs, extracting content, filling forms, and taking screenshots.

## Features

The MCP ChromeDriver server exposes the following tools:

*   `launch_browser`: Launches a Chrome browser instance with a given URL.
*   `goto_page`: Navigates the existing browser instance to a given URL.
*   `close_browser`: Closes the current browser instance.
*   `get_page_source`: Retrieves the source code of the current page.
*   `execute_javascript`: Executes JavaScript code in the current browser instance.
*   `take_screenshot`: Takes a screenshot of the current page and saves it to the downloads directory.
*   `find_element`: Finds an element on the page and returns its text content.
*   `get_element_text`: Retrieves the text content of a specific element.
*   `click_element`: Clicks a specific element on a webpage.
*   `type_into_element`: Types text into a specific element on a webpage.
*   `clear_element_text`: Clears the text from a specific element on a webpage.
*   `scroll`: Scrolls the page by a specified amount.
*   `get_browser_stats`: Retrieves statistics about the current browser state.
*   `get_element_attribute`: Retrieves the value of a specific attribute of an element.
*   `get_elements`: Retrieves a list of elements matching the given locator.
*   `submit_form`: Submits a form element.
*   `wait_for_element`: Waits for an element to be present on the page.
*   `select_option`: Selects an option from a dropdown menu.
*   `upload_file`: Uploads a file to the specified file input element.
*   `open_new_tab`: Opens a new tab with the given URL.
*   `switch_to_tab`: Switches to a specific tab in the browser.
*   `close_tab`: Closes the current tab.
*   `switch_to_frame`: Switches the driver's focus to a particular iframe.
*   `get_current_tab_index`: Returns the index of the currently active tab.

## Installation

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    cd mcp_chromedriver
    ```

2.  Install the dependencies using [uv](https://astral.sh/uv):

    ```bash
    uv sync
    ```

## Usage

1.  Run the MCP ChromeDriver server:

    ```bash
    uv run path/to/mcp_chromedriver/.venv/bin/mcp_chromedriver
    ```

2.  Add the extension to Goose:
    *   Go to Settings > Extensions > Add in Goose.
    *   Set the Type to StandardIO.
    *   Provide an ID, name, and description for your extension.
    *   In the Command field, provide the absolute path to the executable:

        ```text
        uv run /full/path/to/mcp_chromedriver/.venv/bin/mcp_chromedriver
        ```

Now you can use the tools provided by this MCP server in Goose to automate web browsing tasks.
