# pricing_mcp_agent.py
import asyncio
import json
from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server, A2AClient
from python_a2a.mcp import FastMCPAgent, A2AMCPAgent
import nest_asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

nest_asyncio.apply()  # Needed to run interactive python
async def pricing_main(cloud_name: str, filter: str):
    # Connect to the server using SSE
    async with sse_client("http://localhost:8085/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            logger.info("Available tools:")
            for tool in tools_result.tools:
                logger.info(f"  - {tool.name}: {tool.description}")

            # Call our calculator tool
            result = await session.call_tool("get_cloud_price", arguments={"cloud_name": cloud_name, "filter": filter, })
            return result.content[0].text
        

# if __name__ == "__main__":
#     result = asyncio.run(pricing_main("((meterName eq 'Standard Uptime SLA') or (serviceFamily eq 'Compute' and meterName eq 'D16as v4')) and location eq 'US East'"))
#     logger.info(f"Result: {result}\n")

# Pricing Agent for cloud prices
class PricingAgent(A2AServer, FastMCPAgent):
    """Agent that provides cloud price information."""
    
    def __init__(self):
        A2AServer.__init__(self)
        FastMCPAgent.__init__(
            self,
            mcp_servers={"pricing": "http://localhost:8085"}
        )
        logger.info("Pricing MCP Agent initialized with pricing server.")

    def handle_message(self, message):
        if message.content.type == "text":
            logger.info(f"Received message: {message.content.text}")
            filter = message.content.text.strip()
            logger.info(f"Fetching cloud price data for filter: {filter}")

            # Call MCP tool to get price
            # price_info = await self.call_mcp_tool("pricing", "get_cloud_price", cloud_name=cloud_name, "filter": filter, )
            pricing_loaded_json = json.loads(message.content.text)
            price_info = asyncio.run(pricing_main(pricing_loaded_json["cloud_name"], pricing_loaded_json["filter"]))

            return Message(
                content=TextContent(
                    text=price_info
                ),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )
    
        # Handle other message types or errors
        return Message(
            content=TextContent(text="I can provide cloud price information for filters."),
            role=MessageRole.AGENT,
            parent_message_id=message.message_id,
            conversation_id=message.conversation_id
        )

import asyncio
price = PricingAgent()
data = {
    "cloud_name": "azure cloud",
    "filter": "((meterName eq 'Standard Uptime SLA') or (serviceFamily eq 'Compute' and meterName eq 'D16as v4')) and location eq 'US East'"
}
json_str = json.dumps(data)

response = price.handle_message(
    Message(
        content=TextContent(text=json_str),
        role=MessageRole.USER,
        message_id="test-message-id",
        conversation_id="test-conversation-id"
    ))
logger.info(f"Response: {response}\n")

logger.info("Pricing MCP Agent is running on http://0.0.0.0:8084/")
run_server(PricingAgent(), port=8084)