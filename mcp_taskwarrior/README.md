# MCP Taskwarrior Extension

This project provides an MCP server that exposes Taskwarrior commands as MCP tools, allowing you to interact with Taskwarrior through Goose.

## Important Note

Due to the complex nature of Taskwarrior commands, it is highly recommended to consult the `taskwarrior.md` file for detailed information on command syntax, attributes, and usage before attempting to generate task commands.

## Installation

1.  Clone this repository.
2.  Navigate to the project directory.
3.  Set up the project environment using `uv`:

    ```bash
    uv sync
    ```

4.  Activate your virtual environment:

    ```bash
    source .venv/bin/activate
    ```

5.  Install the project locally:

    ```bash
    uv pip install .
    ```

## Usage

1.  Run the server using `mcp dev`:

    ```bash
    mcp dev src/mcp_taskwarrior/server.py
    ```

    Alternatively, you can run the installed package directly:

    ```bash
    uvx mcp-taskwarrior
    ```

2.  To add this MCP server as an extension in Goose:
    *   Go to Settings > Extensions > Add.
    *   Set the Type to StandardIO.
    *   Provide the ID, name, and description for your extension.
    *   In the Command field, provide the absolute path to your executable. For example:

        ```bash
        uv run /full/path/to/mcp-taskwarrior/.venv/bin/mcp-taskwarrior
        ```

3.  Once integrated, you can start using your extension in Goose. Open the Goose chat interface and call your tool as needed.

## Available Tools

*   `list`: Lists tasks, optionally filtered by the given terms.
*   `get_task_data`: Returns task data in JSON format.
*   `get_taskwarrior_md`: Returns the content of taskwarrior.md.
*   `add`: Adds a new task with the given description and optional attributes.
