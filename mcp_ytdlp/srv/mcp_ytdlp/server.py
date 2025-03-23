import yt_dlp
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
import re
import sys

mcp = FastMCP("ytdlp")

def parse_srv3(srv3_data):
    """Parses srv3 data and returns a list of subtitle entries."""
    try:
        import json
        data = json.loads(srv3_data)
        events = data.get('events', [])
        subtitles = []
        for event in events:
            start_ms = event.get('tStartMs', 0)
            duration_ms = event.get('dDurationMs', 0)
            segs = event.get('segs', [])
            # Join the segments, strip whitespace, and filter out empty lines
            text = ' '.join(s.strip() for s in (seg.get('utf8', '') for seg in segs) if s.strip())
            subtitles.append({
                'start': start_ms / 1000.0,
                'duration': duration_ms / 1000.0,
                'text': text
            })
        return subtitles
    except json.JSONDecodeError:
        print("Error decoding srv3 data.")
        return []

def get_automatic_subtitles(url):
    """
    Extracts automatic subtitles from a YouTube video and returns them as a string.

    Args:
        url: The URL of the YouTube video.

    Returns:
        The subtitles as a string, or None if an error occurred.
    """
    ydl_opts = {
        'skip_download': True,  # Skip downloading the video
        'writesubtitles': True,  # Download subtitles (needed to trigger extraction)
        'writeautomaticsub': True,  # Download automatic subtitles
        'subtitlesformat': 'srv3',  # Set subtitle format to srv3
        'outtmpl': '%(title)s-%(id)s.%(ext)s',  # Output filename template (not actually used)
        'no_warnings': True,  # Suppress warnings
        'quiet': True,  # Activate quiet mode
        'subtitleslangs': ['en'], # only get english subs
        'writesubtitles': False, # prevent writing to disk
        'allsubtitles': False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if 'subtitles' in info_dict and 'en' in info_dict['subtitles']:
                sub_info = info_dict['subtitles']['en'][0]
                # Download the subtitle data
                sub_data = ydl.urlopen(sub_info['url']).read().decode('utf-8')
                return sub_data
            elif 'automatic_captions' in info_dict and 'en' in info_dict['automatic_captions']:
                sub_info = info_dict['automatic_captions']['en'][0]
                sub_data = ydl.urlopen(sub_info['url']).read().decode('utf-8')
                return sub_data
            else:
                return "No English automatic subtitles found."
    except yt_dlp.utils.DownloadError as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Error downloading subtitles for {url}: {e}")) from e

@mcp.tool()
def get_automatic_subtitles_tool(url: str) -> str:
    """
    Extracts automatic subtitles from a YouTube video and returns them as a string.

    Args:
        url: The URL of the YouTube video.

    Returns:
        The subtitles as a string, or None if an error occurred.
    """
    subtitles_srv3 = get_automatic_subtitles(url)
    if not subtitles_srv3:
        return "Failed to retrieve subtitles."

    subtitles = parse_srv3(subtitles_srv3)
    if not subtitles:
        return "Failed to parse subtitles."

    all_text = []
    for entry in subtitles:
        text = entry['text']
        if text.strip():  # Only print if the text is not empty after stripping whitespace
            all_text.append(text)
    return "\n".join(all_text)
