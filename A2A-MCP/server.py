# agent1_server.py

import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from python_a2a import A2AServer

# Load any environment variables (e.g., auth tokens)
load_dotenv()

# 1) Create your MCP server and register tools
mcp = FastMCP()

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool()
def square(a: int) -> int:
    """Square a number"""
    return a * a

# 2) Wrap it in an A2A server
#    by default, this will expose:
#      • GET  /.well-known/agent.json   ← AgentCard
#      • POST /                         ← JSON-RPC 2.0 endpoint
#    (per A2A spec, JSON-RPC over HTTP(S))
server = A2AServer(
    host="0.0.0.0",
    port=9000,
    mcp_server=mcp,
    # optional metadata for your AgentCard:
    name="CalculatorAgent",
    description="Exposes simple arithmetic tools via MCP",
)

if __name__ == "__main__":
    server.run()
