import argparse
from .server import mcp

def main():
    """MCP Vollama: Processes images using a local Ollama server."""
    parser = argparse.ArgumentParser(
        description="Processes images from URLs using a local Ollama server."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
