import argparse
from .server import mcp

def main():
    """MCP ChromeDriver: Interact with ChromeDriver to get webpage information."""
    parser = argparse.ArgumentParser(
        description="Interact with ChromeDriver to get webpage information."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
