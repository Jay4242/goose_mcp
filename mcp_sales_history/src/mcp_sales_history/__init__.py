import argparse
from .server import mcp

def main():
    """MCP Sales History: Fetches sales history data from eBay."""
    parser = argparse.ArgumentParser(
        description="Fetches sales history data from eBay for a given search term."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
