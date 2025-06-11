# calculator_agent.py

from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server
from python_a2a.mcp import FastMCPAgent
import re

class CalculatorAgent(A2AServer, FastMCPAgent):
    def __init__(self):
        A2AServer.__init__(self)
        FastMCPAgent.__init__(self, mcp_servers={"calc": "http://localhost:5001"})

    async def handle_message_async(self, message):
        if message.content.type == "text":
            text = message.content.text.lower()

            try:
                if "add" in text:
                    a, b = map(float, re.findall(r"[-+]?\d*\.\d+|\d+", text))
                    result = await self.call_mcp_tool("calc", "add", a=a, b=b)
                elif "subtract" in text:
                    a, b = map(float, re.findall(r"[-+]?\d*\.\d+|\d+", text))
                    result = await self.call_mcp_tool("calc", "subtract", a=a, b=b)
                elif "multiply" in text:
                    a, b = map(float, re.findall(r"[-+]?\d*\.\d+|\d+", text))
                    result = await self.call_mcp_tool("calc", "multiply", a=a, b=b)
                elif "divide" in text:
                    a, b = map(float, re.findall(r"[-+]?\d*\.\d+|\d+", text))
                    result = await self.call_mcp_tool("calc", "divide", a=a, b=b)
                else:
                    return Message(
                        content=TextContent(text="Please use add, subtract, multiply, or divide."),
                        role=MessageRole.AGENT,
                        parent_message_id=message.message_id,
                        conversation_id=message.conversation_id
                    )

                return Message(
                    content=TextContent(text=f"The result is {result}"),
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

# Run server
run_server(CalculatorAgent(), port=5002)
