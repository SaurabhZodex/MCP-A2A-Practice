import os
import sys
import socket
import time
import threading
import argparse
from dotenv import load_dotenv

# python_a2a components
from python_a2a import OpenAIA2AServer, run_server, A2AServer, AgentCard, AgentSkill
from python_a2a.mcp import FastMCP

# ---------------------- Utility Functions ----------------------
def find_available_port(start_port=5000, max_tries=20):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_tries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
    print(f"⚠️  Could not find an available port in range {start_port}-{start_port + max_tries - 1}")
    return start_port + 1000


def run_server_in_thread(server_func, server, *args, **kwargs):
    """Run a server function in a background thread"""
    thread = threading.Thread(target=server_func, args=(server,)+args, kwargs=kwargs, daemon=True)
    thread.start()
    time.sleep(2)
    return thread

# ---------------------- CLI Argument Parsing ----------------------
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="A2A + MCP Agent with add & square tools"
    )
    parser.add_argument("--a2a-port", type=int, default=None,
                        help="Port for A2A server (auto-select if omitted)")
    parser.add_argument("--mcp-port", type=int, default=None,
                        help="Port for MCP server (auto-select if omitted)")
    parser.add_argument("--model", type=str, default="gpt-4o",
                        help="OpenAI model for A2A server (default: gpt-4o)")
    parser.add_argument("--temperature", type=float, default=0.0,
                        help="Temperature for A2A server (default: 0.0)")
    return parser.parse_args()

# ---------------------- Main Application ----------------------
def main():
    load_dotenv()
    # Ensure API key
    if "OPENAI_API_KEY" not in os.environ:
        print("❌ Missing OPENAI_API_KEY environment variable.")
        return 1

    # Parse CLI
    args = parse_arguments()
    a2a_port = args.a2a_port or find_available_port(5000, 20)
    mcp_port = args.mcp_port or find_available_port(7000, 20)
    print(f"🔍 A2A port: {a2a_port}, MCP port: {mcp_port}")

    # ---------------------- Step 1: Setup MCP Server ----------------------
    mcp_server = FastMCP(
        name="CalcTools",
        description="MCP server exposing add and square tools"
    )

    @mcp_server.tool(name="add", description="Add two integers")
    def add(a: int, b: int) -> int:
        return a + b

    @mcp_server.tool(name="square", description="Square an integer")
    def square(a: int) -> int:
        return a * a

    # Start MCP in background
    def run_mcp(mcp_app, host="0.0.0.0", port=mcp_port):
        mcp_app.run(host=host, port=port)
    mcp_thread = run_server_in_thread(run_mcp, mcp_server)

    # ---------------------- Step 2: Setup A2A Server ----------------------
    # Define AgentCard metadata
    agent_card = AgentCard(
        name="CalcAgent",
        description="Agent exposing add & square via MCP",
        url=f"http://localhost:{a2a_port}",
        version="1.0.0",
        skills=[
            AgentSkill(
                name="Addition",
                description="Compute sum of two integers",
                examples=["add(3,5)"]
            ),
            AgentSkill(
                name="Squaring",
                description="Compute square of an integer",
                examples=["square(7)"]
            )
        ]
    )

    # Wrap MCP in A2A Server
    class CalcA2AServer(A2AServer):
        def __init__(self, agent_card, mcp_app):
            super().__init__(agent_card=agent_card)
            self.mcp_app = mcp_app

        def handle_message(self, message):
            # Forward JSON-RPC calls to MCP dispatcher
            return self.mcp_app.handle_message(message)

    a2a_server = CalcA2AServer(agent_card, mcp_server)

    # Configure the underlying LLM
    openai_backend = OpenAIA2AServer(
        api_key=os.environ["OPENAI_API_KEY"],
        model=args.model,
        temperature=args.temperature,
        system_prompt=(
            "You are CalcAgent, able to call add(a,b) and square(a) tools via MCP."
        )
    )
    # Monkey-patch handle_message to the OpenAI backend
    CalcA2AServer.handle_message = lambda self, msg: openai_backend.handle_message(msg)

    # Start A2A in background
    def run_a2a(server, host="0.0.0.0", port=a2a_port):
        run_server(server, host=host, port=port)
    a2a_thread = run_server_in_thread(run_a2a, a2a_server)

    # Keep alive
    print("✅ Servers running. Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
