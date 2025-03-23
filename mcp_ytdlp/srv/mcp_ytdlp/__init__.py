import argparse
from .server import mcp

def main():
    """MCP ytdlp: Extracts automatic subtitles from a YouTube video and converts them to Markdown."""
    parser = argparse.ArgumentParser(
        description="Gives you the ability to extract automatic subtitles from YouTube videos and convert them to Markdown."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
