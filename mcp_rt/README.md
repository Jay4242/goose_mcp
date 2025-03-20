# mcp_rt: Rotten Tomatoes Movie Scraper MCP Server

## Overview

`mcp_rt` is an MCP (Model Context Protocol) server designed to scrape movie data from Rotten Tomatoes. It provides a tool, `get_rotten_tomatoes_movies`, that retrieves a list of currently popular movies, along with their critic and audience scores, sentiments, director(s), actors, and descriptions. This server is intended to be used as an extension for Goose, allowing you to enhance Goose's capabilities with movie-related information.

## Features

- **Scrapes Movie Data:** Retrieves movie information from Rotten Tomatoes, including:
    - Film Title
    - Critic Rating and Sentiment
    - Audience Rating and Sentiment
    - Director(s)
    - Actors
    - Description
- **MCP Compliant:** Built using the `mcp` library, making it easy to integrate with Goose and other MCP-compatible applications.
- **Easy to Use:** Simple command-line interface for running the server.

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)


