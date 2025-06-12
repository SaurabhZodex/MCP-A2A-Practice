# calculator_agent.py

import threading
from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server
from python_a2a.mcp import FastMCPAgent
import re
# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# class CalculatorAgent(A2AServer, FastMCPAgent):
#     def __init__(self):
#         A2AServer.__init__(self)
#         FastMCPAgent.__init__(self, mcp_servers={"calc": "http://localhost:8050/sse"})

#     async def handle_message_async(self, message):
#         if message.content.type == "text":
#             text = message.content.text.lower()
#             logger.info(f"Received message: {text}")
#             if not text:
#                 return Message(
#                     content=TextContent(text="Please provide a valid arithmetic operation."),
#                     role=MessageRole.AGENT,
#                     parent_message_id=message.message_id,
#                     conversation_id=message.conversation_id
#                 )

#             try:
#                 if "add" in text:
#                     a, b = map(float, re.findall(r"[-+]?\d*\.\d+|\d+", text))
#                     result = await self.call_mcp_tool("calc", "add", a=a, b=b)
#                 elif "subtract" in text:
#                     a, b = map(float, re.findall(r"[-+]?\d*\.\d+|\d+", text))
#                     result = await self.call_mcp_tool("calc", "subtract", a=a, b=b)
#                 elif "multiply" in text:
#                     a, b = map(float, re.findall(r"[-+]?\d*\.\d+|\d+", text))
#                     result = await self.call_mcp_tool("calc", "multiply", a=a, b=b)
#                 elif "divide" in text:
#                     a, b = map(float, re.findall(r"[-+]?\d*\.\d+|\d+", text))
#                     result = await self.call_mcp_tool("calc", "divide", a=a, b=b)
#                 else:
#                     return Message(
#                         content=TextContent(text="Please use add, subtract, multiply, or divide."),
#                         role=MessageRole.AGENT,
#                         parent_message_id=message.message_id,
#                         conversation_id=message.conversation_id
#                     )
#                 logger.info(f"Calculated result: {result}")

#                 return Message(
#                     content=TextContent(text=f"The result is {result}"),
#                     role=MessageRole.AGENT,
#                     parent_message_id=message.message_id,
#                     conversation_id=message.conversation_id
#                 )
#             except Exception as e:
#                 return Message(
#                     content=TextContent(text=f"Error: {str(e)}"),
#                     role=MessageRole.AGENT,
#                     parent_message_id=message.message_id,
#                     conversation_id=message.conversation_id
#                 )

# # Run server
# run_server(CalculatorAgent(), port=5002)


# YFinance Agent for stock prices
class YFinanceAgent(A2AServer, FastMCPAgent):
    """Agent that provides stock price information."""
    
    def __init__(self):
        A2AServer.__init__(self)
        FastMCPAgent.__init__(
            self,
            mcp_servers={"finance": "http://localhost:5002"}
        )
        logger.info("YFinance MCP Agent initialized with finance server.")
    
    async def handle_message_async(self, message):
        if message.content.type == "text":
            logger.info(f"Received message: {message.content.text}")
            # Extract ticker from message
            import re
            ticker_match = re.search(r"\b([A-Z]{1,5})\b", message.content.text)
            if ticker_match:
                ticker = ticker_match.group(1)
                
                # Call MCP tool to get price
                price_info = await self.call_mcp_tool("finance", "get_stock_price", ticker=ticker)
                
                if "error" in price_info:
                    return Message(
                        content=TextContent(text=f"Error getting price for {ticker}: {price_info['error']}"),
                        role=MessageRole.AGENT,
                        parent_message_id=message.message_id,
                        conversation_id=message.conversation_id
                    )
                
                return Message(
                    content=TextContent(
                        text=f"{ticker} is currently trading at {price_info['price']:.2f} {price_info['currency']}."
                    ),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id
                )
        
        # Handle other message types or errors
        return Message(
            content=TextContent(text="I can provide stock price information for ticker symbols."),
            role=MessageRole.AGENT,
            parent_message_id=message.message_id,
            conversation_id=message.conversation_id
        )


logger.info("YFinance MCP Agent is running on http://0.0.0.0:5004/")
run_server(YFinanceAgent(), port=5004)