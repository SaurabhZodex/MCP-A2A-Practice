# Import required libraries
from python_a2a.mcp import FastMCP, text_response

# Create a new MCP server
calculator_mcp = FastMCP(
    name="Calculator MCP",
    version="1.0.0",
    description="Provides mathematical calculation functions"
)

# Define tools using simple decorators with type hints
@calculator_mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@calculator_mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b

@calculator_mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

@calculator_mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        return text_response("Cannot divide by zero")
    return a / b

# For Jupyter Notebook, use this cell to start the server in a non-blocking way
# This will run the server in a separate thread
import threading

# Define a function to run the server in a thread
def run_server():
    calculator_mcp.run(host="0.0.0.0", port=5001)

# Start the server in a background thread
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

print("Calculator MCP server is running on http://0.0.0.0:5001")

# To test the tools directly in the notebook
# Example usage:
print("Testing add function:", add(5, 3))
print("Testing subtract function:", subtract(10, 4))
print("Testing multiply function:", multiply(6, 7))
print("Testing divide function:", divide(20, 5))
print("Testing divide by zero:", divide(10, 0))