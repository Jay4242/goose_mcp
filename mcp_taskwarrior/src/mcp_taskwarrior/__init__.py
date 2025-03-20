import argparse
from .server import mcp

def main():
    """MCP Taskwarrior: Exposes Taskwarrior commands as MCP tools."""
    parser = argparse.ArgumentParser(
        description="Exposes Taskwarrior commands as MCP tools."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
