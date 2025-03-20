import argparse
from .server import mcp

def main():
    """MCP SearxNG: Searches the web using a SearxNG instance."""
    parser = argparse.ArgumentParser(
        description="Searches the web using a SearxNG instance."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
