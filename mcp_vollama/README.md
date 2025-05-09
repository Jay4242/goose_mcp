# MCP Vollama

This is an MCP (Model Context Protocol) server that processes images using a local Ollama server. It allows you to send one or two image URLs and up to three prompts to the server, which will then use Ollama to analyze the images and return a text response. The prompts are interleaved with the images in the order they are provided.

## Prerequisites

*   [uv](https://docs.astral.sh/uv/):  Make sure you have uv installed.
*   [Ollama](https://ollama.com/): You need a working Ollama installation with a vision model available.

## Installation

1.  Clone the repository.
2.  Navigate to the project directory.
3.  Create a virtual environment and install the dependencies using `uv sync`.

    ```bash
    uv sync
    ```

## Configuration

Before running the server, you need to set the `OLLAMA_BASE_URL` environment variable to the address of your Ollama server. For example:

```bash
export OLLAMA_BASE_URL=http://localhost:11434
```
