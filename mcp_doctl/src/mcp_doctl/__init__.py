import argparse
from .server import mcp

def main():
    """MCP Doctl: Manage DigitalOcean resources using doctl."""
    parser = argparse.ArgumentParser(
        description="Gives you the ability to manage DigitalOcean resources using doctl."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
