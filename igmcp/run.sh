#!/bin/bash
# Starts ig-mcp from its own folder so it finds its .env file.
cd "$(dirname "$0")" && exec ./.venv/bin/python -m src.instagram_mcp_server
