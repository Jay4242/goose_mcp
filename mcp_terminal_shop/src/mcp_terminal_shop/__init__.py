import argparse
from .server import mcp
def main():
    """MCP Terminal Shop: Order coffee from your terminal."""
    parser = argparse.ArgumentParser(
        description="Gives you the ability to order coffee from your terminal."
    )
    parser.parse_args()
    mcp.run()
if __name__ == "__main__":
    main()
