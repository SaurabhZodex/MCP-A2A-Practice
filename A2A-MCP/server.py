# agent1.py
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from python_a2a.agent import A2AAgent
import uvicorn

app = FastAPI()
mcp = FastMCP(app, name="CalculatorAgent")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool()
def square(a: int) -> int:
    """Square number"""
    return a * a

agent = A2AAgent(name="CalculatorAgent", mcp=mcp)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
