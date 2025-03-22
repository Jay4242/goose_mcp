import base64
import io
import requests
import os
from openai import OpenAI
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from PIL import Image
import httpx

mcp = FastMCP("vollama")

@mcp.tool()
def process_image(image_url: str, prompt: str) -> str:
    """
    Processes an image from a URL using a local Ollama server and returns the text response.

    Args:
        image_url: The URL of the image.
        prompt: The prompt to send to the Ollama server.

    Returns:
        The text response from the Ollama server.
    """
    try:
        # Validate that the URL starts with http or https
        if not image_url.startswith("http://") and not image_url.startswith("https://"):
            return "Invalid image URL. Must start with http:// or https://"

        # Download the image
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(image_url, stream=True, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        # Verify that the content type is an image
        content_type = response.headers['Content-Type']
        print(f"Content type: {content_type}")  # Log the content type
        if not content_type.startswith('image/'):
            return f"Invalid content type: {content_type}. URL must point to an image."

        # Open the image using PIL
        try:
            image = Image.open(io.BytesIO(response.content))
        except Exception as e:
            return f"Error processing image: cannot identify image file. PIL error: {str(e)}"

        # Convert the image to JPEG or PNG if necessary
        if image.format not in ("JPEG", "PNG"):
            image = image.convert("RGB")  # Convert to RGB if necessary
            image_format = "JPEG"
        else:
            image_format = image.format

        # Save the image to a BytesIO object
        buffered = io.BytesIO()
        image.save(buffered, format=image_format)
        base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Get the base URL from the environment variable
        base_url = os.environ.get("OLLAMA_BASE_URL")
        if not base_url:
            return "OLLAMA_BASE_URL environment variable not set."

        # Point to the local Ollama server
        client = OpenAI(base_url=base_url, api_key="None", timeout=httpx.Timeout(420))

        # Model selection
        model = "gemma3:4b-it-q8_0"

        # Create the completion request
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image_format.lower()};base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=-1,
            stream=False
        )

        # Extract and return the response
        return completion.choices[0].message.content.strip()

    except requests.exceptions.RequestException as e:
        return f"Error downloading image: {str(e)}"
    except FileNotFoundError:
        return "Image file not found."
    except Exception as e:
        return f"Error processing image: {str(e)}"
