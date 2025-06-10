from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv("../.env")

# Create an MCP server
mcp = FastMCP(
    name="square_number",
    instructions="This server provides a tool to square a number.",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8051,  # only used for SSE transport (set this to any port)
)


# Add a simple calculator tool
@mcp.tool()
def square(a: int) -> int:
    """Square number"""
    return a*a


# Run the server
if __name__ == "__main__":
    transport = "sse"
    if transport == "stdio":
        print("Running server with stdio transport")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Running server with SSE transport")
        mcp.run(transport="sse")
    else:
        raise ValueError(f"Unknown transport: {transport}")