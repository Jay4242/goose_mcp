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
from typing import List, Tuple, Optional

mcp = FastMCP("vollama")

@mcp.tool()
def process_image(prompts: List[str], image_urls: List[str]) -> str:
    """
    Processes one or two images from URLs using a local Ollama server, along with 1-3 prompts, and returns the text response.

    Args:
        prompts: A list of strings, where each string is a prompt.  A maximum of three prompts can be provided.
        image_urls: A list of strings, where each string is a URL to an image. A maximum of two image URLs can be provided.

    Returns:
        The text response from the Ollama server.
    """
    try:
        # Validate the number of prompts and image URLs
        if not prompts or not image_urls:
            return "Must provide at least one prompt and one image URL."

        if len(image_urls) > 2:
            return "A maximum of two image URLs can be provided."

        if len(prompts) > 3:
            return "A maximum of three prompts can be provided."

        # Download and encode images
        base64_images: List[str] = []
        image_formats: List[str] = []

        for image_url in image_urls:
            # Validate that the URL starts with http or https
            if not image_url.startswith("http://") and not image_url.startswith("https://"):
                return f"Invalid image URL: {image_url}. Must start with http:// or https://"

            # Download the image
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
            response = requests.get(image_url, stream=True, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            # Verify that the content type is an image
            content_type = response.headers['Content-Type']
            print(f"Content type: {content_type}")  # Log the content type
            if not content_type.startswith('image/'):
                return f"Invalid content type: {content_type} for URL {image_url}. URL must point to an image."

            # Open the image using PIL
            try:
                image = Image.open(io.BytesIO(response.content))
            except Exception as e:
                return f"Error processing image from URL {image_url}: cannot identify image file. PIL error: {str(e)}"

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

            base64_images.append(base64_image)
            image_formats.append(image_format)

        # Get the base URL from the environment variable
        base_url = os.environ.get("OLLAMA_BASE_URL")
        if not base_url:
            return "OLLAMA_BASE_URL environment variable not set."

        # Point to the local Ollama server
        client = OpenAI(base_url=base_url, api_key="None", timeout=httpx.Timeout(420))

        # Model selection
        model = "gemma3:4b-it-q8_0"

        # Build the messages list
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        for i in range(len(prompts)):
            messages.append({"role": "user", "content": [{"type": "text", "text": prompts[i]}]})
            if i < len(base64_images):
                messages[-1]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{image_formats[i].lower()};base64,{base64_images[i]}"
                    },
                })

        # Create the completion request
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
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
