# db_mcp_agent.py
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
async def db_main(cloud_name: str, service_name: str):
    # Connect to the server using SSE
    async with sse_client("http://localhost:8083/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # # List available tools
            # tools_result = await session.list_tools()
            # logger.info("Available tools:")
            # for tool in tools_result.tools:
            #     logger.info(f"  - {tool.name}: {tool.description}")

            # Call our calculator tool
            result = await session.call_tool("search_api_filter", arguments={"cloud_name": cloud_name, "service_name": service_name})
            return result.content[0].text

# if __name__ == "__main__":
#     result = asyncio.run(db_main("Azure Cloud"))
#     logger.info(f"Result: {result}\n")

# DB Agent for ticker lookup
class DBAgent(A2AServer, FastMCPAgent):
    """Agent that finds API filter."""
    def __init__(self):
        A2AServer.__init__(self)
        FastMCPAgent.__init__(
            self,
            mcp_servers={"filter": "http://localhost:8083"}
        )
        logger.info("DB MCP Agent initialized with search server.\n")

    def handle_message(self, message):
        if message.content.type == "text":
            logger.info(f"Received message: {message.content.text}")

            # Call MCP tool to lookup API filter
            # api_filter = await self.call_mcp_tool("cloud_name", "search_api_filter", query=message.content.text)
            db_loaded_json = json.loads(message.content.text)
            api_filter = asyncio.run(db_main(db_loaded_json["cloud_name"], db_loaded_json["service_name"]))

            return Message(
                content=TextContent(text=f"{api_filter}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )
        
        # Handle other message types or errors
        return Message(
            content=TextContent(text="I can help find API filter for cloud."),
            role=MessageRole.AGENT,
            parent_message_id=message.message_id,
            conversation_id=message.conversation_id
        )

import asyncio
db = DBAgent()
data = {
    "cloud_name": "azure cloud",
    "service_name": "kf+ops"
}
json_str = json.dumps(data)
response = db.handle_message(
    Message(
        content=TextContent(text=json_str),
        role=MessageRole.USER,
        message_id="test-message-id",
        conversation_id="test-conversation-id"
    ))
logger.info(f"Response: {response}\n")

logger.info("DB MCP Agent is running on http://0.0.0.0:8082/")
run_server(DBAgent(), port=8082)
