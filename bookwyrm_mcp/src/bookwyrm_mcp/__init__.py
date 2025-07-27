import argparse
from .server import mcp
def main():
    """MCP Bookwyrm: Interact with Bookwyrm for user and book information."""
    parser = argparse.ArgumentParser(
        description="Gives you the ability to interact with Bookwyrm for user and book information."
    )
    parser.parse_args()
    mcp.run()
if __name__ == "__main__":
    main()
