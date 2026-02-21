import logging
import os

# Configure logging to a file in the same directory
log_file = os.path.join(os.path.dirname(__file__), "server.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("my-simple-server")
logger.info("Server starting...")

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("My Simple Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two numbers"""
    logger.info(f"Adding {a} and {b}")
    return a * b

@mcp.tool()
def echo(text: str) -> str:
    """Echoes the input text"""
    logger.info(f"Echoing: {text}")
    return f"You said: {text}"

if __name__ == "__main__":
    import os
    # Detect if we are running in a cloud environment like Render
    if os.getenv("RENDER") or os.getenv("PORT"):
        port = int(os.getenv("PORT", 8000))
        logger.info(f"Running server on SSE transport at port {port}")
        mcp.run(transport="sse", port=port)
    else:
        logger.info("Running server on stdio")
        mcp.run(transport="stdio")
