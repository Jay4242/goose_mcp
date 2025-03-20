import argparse
from .server import mcp

def main():
    """MCP Fark: Fetches and parses headlines from Fark.com."""
    parser = argparse.ArgumentParser(
        description="Fetches and parses headlines from Fark.com."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
