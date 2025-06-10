import threading
import time
from dotenv import load_dotenv
from python_a2a import run_server, A2AServer, AgentCard, AgentSkill
from python_a2a.mcp import FastMCP

# Load environment variables if needed
load_dotenv()

# =================== MCP Server Setup ===================
# MCP Server 1 with 'add' tool
mcp1 = FastMCP(port=8001)

@mcp1.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

# MCP Server 2 with 'square' tool
mcp2 = FastMCP(port=8002)

@mcp2.tool()
def square(a: int) -> int:
    """Square a number"""
    return a * a

# =================== A2A Server Setup ===================
# Start A2A server to enable agent-to-agent communication
a2a_server = A2AServer(port=9000)

# Register Agent 1 (Calculator Add)
agent1_card = AgentCard(
    id="agent-add",
    name="Addition Agent",
    description="Agent to add two numbers",
    mcp_url="http://localhost:8001"
)

# Register Agent 2 (Calculator Square)
agent2_card = AgentCard(
    id="agent-square",
    name="Square Agent",
    description="Agent to square a number",
    mcp_url="http://localhost:8002"
)

a2a_server.register(agent1_card)
a2a_server.register(agent2_card)

# =================== Server Threads ===================
def run_mcp1():
    mcp1.serve()

def run_mcp2():
    mcp2.serve()

def run_a2a():
    run_server(a2a_server)

# Start all servers in separate threads
threading.Thread(target=run_mcp1, daemon=True).start()
threading.Thread(target=run_mcp2, daemon=True).start()
threading.Thread(target=run_a2a, daemon=True).start()

time.sleep(2)  # Give servers time to start

# =================== Agent-to-Agent Example ===================
# Agent 1 calls Agent 2's square function via A2A
from python_a2a import A2AClient

client = A2AClient(a2a_server_url="http://localhost:9000")

# Call 'add' tool from Agent 1
add_result = client.call_agent(
    agent_id="agent-add",
    tool_name="add",
    tool_args={"a": 5, "b": 7}
)
print(f"Add Result: {add_result}")

# Call 'square' tool from Agent 2
square_result = client.call_agent(
    agent_id="agent-square",
    tool_name="square",
    tool_args={"a": 4}
)
print(f"Square Result: {square_result}")

# Keep main thread alive
while True:
    time.sleep(5)
