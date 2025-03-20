import argparse
from mcp_rt.server import mcp

def main():
    """MCP Rotten Tomatoes: Scrapes movie information from Rotten Tomatoes."""
    parser = argparse.ArgumentParser(
        description="Gives you the ability to scrape movie information from Rotten Tomatoes."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
