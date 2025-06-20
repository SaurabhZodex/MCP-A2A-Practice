# # # calculator_client.py

# # from python_a2a import A2AClient, Message, TextContent, MessageRole
# # import argparse

# # def interactive_session(client):
# #     print("Calculator Assistant (type 'exit' to quit)")
# #     while True:
# #         user_input = input("> ")
# #         if user_input.lower() in ("exit", "quit"):
# #             break
# #         message = Message(content=TextContent(text=user_input), role=MessageRole.USER)
# #         print(f"You: {user_input}")
# #         response = client.send_message(message)
# #         print(f"Assistant: {response.content.text}")

# # if __name__ == "__main__":
# #     parser = argparse.ArgumentParser()
# #     parser.add_argument("--endpoint", default="http://localhost:5000/a2a")
# #     args = parser.parse_args()

# #     client = A2AClient(args.endpoint)
# #     print(f"Connecting to A2A endpoint: {args.endpoint}")
# #     try:
# #         agent_card = client.get_agent_card()
# #         print(f"Connected to agent: {agent_card.name} ({agent_card.description})")
# #     except Exception as e:
# #         print(f"Failed to get agent card: {e}")
# #         exit(1)
# #     interactive_session(client)

# from python_a2a import A2AClient, Message, TextContent, MessageRole
# import argparse

# def interactive_session(client):
#     """Interactive session with the stock assistant."""
#     print("\n===== Stock Price Assistant =====")
#     print("Type 'exit' or 'quit' to end the session.")
#     print("Example queries:")
#     print("  - What's the stock price of Apple?")
#     print("  - How much is Microsoft trading for?")
#     print("  - Get the current price of Tesla stock")
#     print("=" * 50)
    
#     while True:
#         try:
#             user_input = input("\n> ")
            
#             if user_input.lower() in ["exit", "quit"]:
#                 print("Goodbye!")
#                 break
            
#             # Send as a text message
#             message = Message(
#                 content=TextContent(text=user_input),
#                 role=MessageRole.USER
#             )
            
#             print("Sending to assistant...")
#             response = client.send_message(message)
#             print(f"Response received: {response}")

#             print(f"\nYou: {user_input}")
#             if response.content.type != "text":
#                 print("Received non-text response, please try again.")
#                 continue

#             # Display the response
#             print(f"Assistant: {response.content.text}")
            
#         except Exception as e:
#             print(f"Error: {e}")
#             print("Please try again or type 'exit' to quit.")
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Stock Assistant Client")
#     parser.add_argument("--endpoint", default="http://localhost:5000/a2a", 
#                         help="Stock assistant endpoint URL")
    
#     args = parser.parse_args()
#     print(f"Connecting to A2A endpoint: {args.endpoint}")
#     # Create a client
#     client = A2AClient(args.endpoint)
    
#     # Start interactive session
#     interactive_session(client)

# calculator_agent.py
import threading
from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server, A2AClient
from python_a2a.mcp import FastMCPAgent
import re
# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

duckduckgo_endpoint="http://127.0.0.1:5003/a2a"
duckduckgo_client = A2AClient(duckduckgo_endpoint)
ticker_message = Message(
    content=TextContent(text=f"What's the ticker for Apple?"),
    role=MessageRole.USER
)
response = duckduckgo_client.send_message(ticker_message)
logger.info(response)
logger.info(response.content.text)