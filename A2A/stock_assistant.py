# calculator_assistant.py

from python_a2a import OllamaA2AServer, OpenAIA2AServer, A2AClient, Message, TextContent, MessageRole, run_server
import os
from dotenv import load_dotenv
# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# class CalculatorAssistant(OllamaA2AServer):
#     def __init__(self, api_key, calc_agent_url):
#         super().__init__(
#             api_url="http://localhost:11434",  # Required for Ollama connection
#             model="gemma3:1b",
#             system_prompt="You are a calculator assistant. You convert queries into arithmetic operations using specialized agents."
#         )
#         self.calc_client = A2AClient(calc_agent_url)

#     def handle_message(self, message):
#         if message.content.type == "text":
#             return self._handle_calc_query(message)
#         return super().handle_message(message)

#     def _handle_calc_query(self, message):
#         try:
#             # Use OpenAI to extract arithmetic intent
#             ollama_response = super().handle_message(
#                 Message(
#                     content=TextContent(
#                         text=f"Convert the following into a basic operation (add, subtract, multiply, divide): '{message.content.text}'"
#                     ),
#                     role=MessageRole.USER
#                 )
#             )

#             operation_text = ollama_response.content.text.strip()

#             # Forward to calculator agent
#             response = self.calc_client.send_message(
#                 Message(
#                     content=TextContent(text=operation_text),
#                     role=MessageRole.USER
#                 )
#             )

#             logger.info(f"Received response from calculator agent: {response.content.text}")
#             logger.info(Message(
#                     content=TextContent(text=response.content.text),
#                     role=MessageRole.AGENT,
#                     parent_message_id=message.message_id,
#                     conversation_id=message.conversation_id
#                 ))

#             return Message(
#                 content=TextContent(text=f"Result: {response.content.text}"),
#                 role=MessageRole.AGENT,
#                 parent_message_id=message.message_id,
#                 conversation_id=message.conversation_id
#             )
#         except Exception as e:
#             return Message(
#                 content=TextContent(text=f"Error: {str(e)}"),
#                 role=MessageRole.AGENT,
#                 parent_message_id=message.message_id,
#                 conversation_id=message.conversation_id
#             )

# # Run assistant
# if __name__ == "__main__":   
#     load_dotenv() 
#     api_key = os.getenv("OPENAI_API_KEY")
#     print(api_key)

#     if not api_key:
#         print("Set OPENAI_API_KEY first.")
#         exit(1)

#     assistant = CalculatorAssistant(
#         api_key=api_key,
#         calc_agent_url="http://localhost:5002/a2a"  # URL of the calculator agent MCP server
#     )
#     run_server(assistant, port=5000)


from python_a2a import A2AClient, Message, TextContent, MessageRole, OpenAIA2AServer, run_server
import re
import os

class StockAssistant(OllamaA2AServer):
    """An AI assistant for stock information that coordinates specialized agents."""
    
    def __init__(self, api_key, duckduckgo_endpoint, yfinance_endpoint):
        # Initialize the OpenAI-powered agent
        super().__init__(
            api_url="http://localhost:11434",  # Required for Ollama connection
            model="gemma3:1b",
            system_prompt=(
                "You are a helpful financial assistant that helps users get stock information. "
                "You extract company names from user queries to find ticker symbols and prices."
            )
        )
        
        # Create clients for connecting to specialized agents
        self.duckduckgo_client = A2AClient(duckduckgo_endpoint)
        self.yfinance_client = A2AClient(yfinance_endpoint)
    
    def handle_message(self, message):
        """Override to intercept stock-related queries."""
        if message.content.type == "text":
            text = message.content.text.lower()
            logger.info(f"Received message: {text}")
            
            # Check if this is a stock price query
            if ("stock" in text or "price" in text or "trading" in text) and any(company in text for company in ["apple", "microsoft", "google", "amazon", "tesla", "facebook", "meta"]):
                # Process as a stock query
                return self._get_stock_info(message)
        
        # For all other messages, defer to OpenAI
        return super().handle_message(message)
    
    def _get_stock_info(self, message):
        """Process a stock information query by coordinating with specialized agents."""
        try:
            # First, use OpenAI to extract the company name
            ollama_response = super().handle_message(Message(
                content=TextContent(
                    text=f"Extract only the company name from this query: '{message.content.text}'. "
                         f"Return ONLY the company name, nothing else."
                ),
                role=MessageRole.USER
            ))
            
            company_name = ollama_response.content.text.strip()
            company_name = company_name.strip('"\'.,')
            logger.info(f"Extracted company name: {company_name}")
            
            # Step 1: Get the ticker symbol from DuckDuckGo agent
            ticker_message = Message(
                content=TextContent(text=f"What's the ticker for {company_name}?"),
                role=MessageRole.USER
            )
            ticker_response = self.duckduckgo_client.send_message(ticker_message)
            logger.info(f"Ticker response: {ticker_response.content.text}")
            
            # Extract ticker from response
            ticker_match = re.search(r'ticker\s+(?:symbol\s+)?(?:for\s+[\w\s]+\s+)?is\s+([A-Z]{1,5})', 
                                   ticker_response.content.text, re.I)
            if not ticker_match:
                return Message(
                    content=TextContent(text=f"I couldn't find the ticker symbol for {company_name}."),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id
                )
            
            ticker = ticker_match.group(1)
            logger.info(f"Found ticker: {ticker}")
            
            # Step 2: Get the stock price from YFinance agent
            price_message = Message(
                content=TextContent(text=f"What's the current price of {ticker}?"),
                role=MessageRole.USER
            )
            price_response = self.yfinance_client.send_message(price_message)
            logger.info(f"Price response: {price_response.content.text}")

            # Return the combined information
            return Message(
                content=TextContent(
                    text=f"{company_name} ({ticker}): {price_response.content.text}"
                ),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )
            
        except Exception as e:
            # Handle any errors
            return Message(
                content=TextContent(text=f"Sorry, I encountered an error: {str(e)}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )
# Run the assistant
if __name__ == "__main__":
    # api_key = os.environ.get("OPENAI_API_KEY")
    # if not api_key:
    #     print("Error: OPENAI_API_KEY environment variable is required")
    #     exit(1)
    
    assistant = StockAssistant(
        api_key="api_key",
        duckduckgo_endpoint="http://localhost:5003/a2a",
        yfinance_endpoint="http://localhost:5004/a2a"
    )
    
    run_server(assistant, port=5000)