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
        response = client.send_message(message)
        print(f"Assistant: {response.content.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://localhost:5000/a2a")
    args = parser.parse_args()

    client = A2AClient(args.endpoint)
    interactive_session(client)
