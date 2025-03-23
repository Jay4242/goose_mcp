# mcp_ytdlp

This is an MCP (Model Context Protocol) server that extracts automatic subtitles from YouTube videos using yt-dlp. It is designed to be used with Goose, allowing Goose to access and utilize subtitles from YouTube videos.

## Usage

1.  Clone this repository.
2.  Run `uv sync` to create a virtual environment and install the necessary dependencies.
3.  Add the extension to your Goose instance by going to Settings > Extensions > Add.
4.  Set the Type to StandardIO.
5.  Provide an ID, name, and description for your extension.
6.  In the Command field, provide the absolute path to your executable. For example: `uv run /path/to/mcp_ytdlp/.venv/bin/mcp_ytdlp`

Now Goose can use the `get_automatic_subtitles_tool` to extract subtitles from YouTube videos!
