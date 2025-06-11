# calculator_assistant.py

from python_a2a import OllamaA2AServer, OpenAIA2AServer, A2AClient, Message, TextContent, MessageRole, run_server
import os
from dotenv import load_dotenv


class CalculatorAssistant(OllamaA2AServer):
    def __init__(self, api_key, calc_agent_url):
        super().__init__(
            api_url="http://localhost:11434",  # Required for Ollama connection
            model="gemma3:1b",
            system_prompt="You are a calculator assistant. You convert queries into arithmetic operations using specialized agents."
        )
        self.calc_client = A2AClient(calc_agent_url)

    def handle_message(self, message):
        if message.content.type == "text":
            return self._handle_calc_query(message)
        return super().handle_message(message)

    def _handle_calc_query(self, message):
        try:
            # Use OpenAI to extract arithmetic intent
            openai_response = super().handle_message(
                Message(
                    content=TextContent(
                        text=f"Convert the following into a basic operation (add, subtract, multiply, divide): '{message.content.text}'"
                    ),
                    role=MessageRole.USER
                )
            )

            operation_text = openai_response.content.text.strip()

            # Forward to calculator agent
            response = self.calc_client.send_message(
                Message(
                    content=TextContent(text=operation_text),
                    role=MessageRole.USER
                )
            )

            return Message(
                content=TextContent(text=f"Result: {response.content.text}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )
        except Exception as e:
            return Message(
                content=TextContent(text=f"Error: {str(e)}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )

# Run assistant
if __name__ == "__main__":   
    load_dotenv() 
    api_key = os.getenv("OPENAI_API_KEY")
    print(api_key)

    if not api_key:
        print("Set OPENAI_API_KEY first.")
        exit(1)

    assistant = CalculatorAssistant(
        api_key=api_key,
        calc_agent_url="http://localhost:5002/a2a"
    )
    run_server(assistant, port=5000)
