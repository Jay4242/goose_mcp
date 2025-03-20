# goose_mcp

An attempt at MCP servers for [Goose](https://github.com/block/goose)

I tried to follow their [custom-extensions guide](https://block.github.io/goose/docs/tutorials/custom-extensions)

Running `uv sync` in each directory creates the Python .venv environment for each mcp.

From there you can add the `uv run /foo/bar/path/to/mcp_server/.venv/bin/mcp_server_name` command to your `goose configure` and it should show up in your goose.

> The only thing not afraid of Canada Mooses, is Canada Gooses.
