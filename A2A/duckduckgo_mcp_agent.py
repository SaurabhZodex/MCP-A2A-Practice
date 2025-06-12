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

# DuckDuckGo Agent for ticker lookup
class DuckDuckGoAgent(A2AServer, FastMCPAgent):
    """Agent that finds stock ticker symbols."""
    
    def __init__(self):
        A2AServer.__init__(self)
        FastMCPAgent.__init__(
            self,
            mcp_servers={"search": "http://localhost:5001"}
        )
        logger.info("DuckDuckGo MCP Agent initialized with search server.")
    
    async def handle_message_async(self, message):
        if message.content.type == "text":
            logger.info(f"Received message: {message.content.text}")
            # Extract company name from message
            company_match = re.search(r"ticker\s+(?:for|of)\s+([A-Za-z\s]+)", message.content.text, re.I)
            if company_match:
                company_name = company_match.group(1).strip()
            else:
                # Default to using the whole message
                company_name = message.content.text.strip()
            
            # Call MCP tool to lookup ticker
            ticker = await self.call_mcp_tool("search", "search_ticker", company_name=company_name)
            
            return Message(
                content=TextContent(text=f"The ticker symbol for {company_name} is {ticker}."),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )
        
        # Handle other message types or errors
        return Message(
            content=TextContent(text="I can help find ticker symbols for companies."),
            role=MessageRole.AGENT,
            parent_message_id=message.message_id,
            conversation_id=message.conversation_id
        )
    
logger.info("DuckDuckGo MCP Agent is running on http://0.0.0.0:5003/")
run_server(DuckDuckGoAgent(), port=5003)
