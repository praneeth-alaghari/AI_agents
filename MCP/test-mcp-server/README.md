# Simple MCP Server

A basic Model Context Protocol (MCP) server built with Python and FastMCP.

## Setup

1. Install dependencies:
   ```bash
   pip install mcp[cli]
   ```

2. Run the server:
   ```bash
   python server.py
   ```

## Tools

- `add(a, b)`: Adds two integers and returns the result.
- `echo(text)`: Returns the input text prefixed with "You said: ".

## Integration with Antigravity / Claude Desktop

To use this server in an IDE or client, add the following configuration:

```json
{
  "mcpServers": {
    "my-simple-server": {
      "command": "C:/code_repo/AI_agents/MCP/venv/Scripts/python.exe",
      "args": ["C:/code_repo/AI_agents/MCP/server.py"]
    }
  }
}
```
