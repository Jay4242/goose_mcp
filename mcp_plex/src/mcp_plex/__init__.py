import argparse
from .server import mcp

def main():
    """MCP Plex: Interact with Plex Media Server."""
    parser = argparse.ArgumentParser(
        description="Gives you the ability to interact with Plex."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
