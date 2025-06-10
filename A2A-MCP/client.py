import threading
import time
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import python_a2a

# Define shared tools (must be at top level)
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

def square(a: int) -> int:
    """Square number"""
    return a * a

def run_agent(agent_name: str, port: int, other_port: int, other_alias: str):
    """Start an MCP agent with tools and connect to another agent via A2A"""
    # Create MCP instance
    mcp_server = FastMCP(agent_name, port=port)
    
    # Register tools using the standard function registration
    mcp_server.tool()(add)
    mcp_server.tool()(square)
    
    # Start server in a daemon thread
    server_thread = threading.Thread(
        target=mcp_server.run,
        daemon=True
    )
    server_thread.start()
    
    # Wait for server initialization
    time.sleep(2)  
    print(f"{agent_name} started on port {port}")

    # Connect to the other agent using A2A
    print(f"{agent_name} connecting to {other_alias} at port {other_port}...")
    python_a2a.connect(f"http://localhost:{other_port}", alias=other_alias)
    print(f"{agent_name} successfully connected to {other_alias}")

    # Keep agent running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"Shutting down {agent_name}")

if __name__ == "__main__":
    load_dotenv()  # Load environment variables

    # Configure agents
    agents = [
        {"agent_name": "Agent1", "port": 8000, "other_port": 8001, "other_alias": "Agent2"},
        {"agent_name": "Agent2", "port": 8001, "other_port": 8000, "other_alias": "Agent1"}
    ]

    # Start agents in separate threads
    threads = []
    for agent in agents:
        t = threading.Thread(target=run_agent, kwargs=agent)
        t.start()
        threads.append(t)

    # Wait for termination
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("Shutting down all agents")