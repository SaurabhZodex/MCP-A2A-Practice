# calculator_client.py

from python_a2a import A2AClient, Message, TextContent, MessageRole
import argparse

def interactive_session(client):
    print("Calculator Assistant (type 'exit' to quit)")
    while True:
        user_input = input("> ")
        if user_input.lower() in ("exit", "quit"):
            break
        message = Message(content=TextContent(text=user_input), role=MessageRole.USER)
        print(f"You: {user_input}")
        response = client.send_message(message)
        print(f"Assistant: {response.content.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://localhost:5000/a2a")
    args = parser.parse_args()

    client = A2AClient(args.endpoint)
    print(f"Connecting to A2A endpoint: {args.endpoint}")
    try:
        agent_card = client.get_agent_card()
        print(f"Connected to agent: {agent_card.name} ({agent_card.description})")
    except Exception as e:
        print(f"Failed to get agent card: {e}")
        exit(1)
    interactive_session(client)