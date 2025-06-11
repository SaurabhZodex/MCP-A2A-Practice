from python_a2a import run_server, AgentCard, AgentSkill
from python_a2a.mcp import FastMCP
import threading

# -------------------- Agent 2: Square Service --------------------
agent2_mcp = FastMCP(
    name="SquareAgent",
    version="1.0.0",
    description="Squares a number provided"
)

@agent2_mcp.tool()
def square(x: float) -> float:
    """Return the square of x"""
    return x * x

# Run Agent 2 MCP server on port 8002
def start_agent2():
    run_server(
        mcp=agent2_mcp,
        host="127.0.0.1",
        port=8002
    )

# -------------------- Agent 1: Add Service + A2A call to Agent 2 --------------------
agent1_mcp = FastMCP(
    name="AddAgent",
    version="1.0.0",
    description="Adds two numbers and then squares the result via Agent 2"
)

# Create an AgentCard for Agent 2 (A2A client)
agent2_card = AgentCard(
    name="SquareAgent",
    url="http://127.0.0.1:8002/a2a"
)
# Define the AgentSkill for the 'square' tool on Agent 2
square_skill = AgentSkill(
    name="square",
    agent_card=agent2_card
)

@agent1_mcp.tool()
def add_and_square(a: float, b: float) -> float:
    """
    Adds two numbers (a + b) and then uses Agent 2 via A2A to square the sum.
    """
    # First, add locally
    sum_result = a + b
    # Then call Agent 2's square skill
    squared = square_skill.invoke(sum_result)
    return squared

# Run Agent 1 MCP server on port 8001
def start_agent1():
    run_server(
        mcp=agent1_mcp,
        host="127.0.0.1",
        port=8001
    )

if __name__ == "__main__":
    # Start both agents in separate threads
    t2 = threading.Thread(target=start_agent2, daemon=True)
    t1 = threading.Thread(target=start_agent1, daemon=True)
    t2.start()
    t1.start()

    print("Agent 1 (AddAgent) running on http://127.0.0.1:8001/mcp")
    print("Agent 2 (SquareAgent) running on http://127.0.0.1:8002/mcp")

    # Keep the main thread alive
    threading.Event().wait()
