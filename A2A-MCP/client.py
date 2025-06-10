from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server
from python_a2a.mcp import FastMCPAgent

class CalculatorAgent(A2AServer, FastMCPAgent):
    """A calculator agent that uses MCP tools."""
    
    def __init__(self):
        # Initialize both parent classes
        A2AServer.__init__(self)
        FastMCPAgent.__init__(
            self,
            mcp_servers={"calc": "http://localhost:5001"}  # Connect to our MCP server
        )
    
    async def handle_message_async(self, message):
        """Process messages and use MCP tools."""
        try:
            if message.content.type == "text":
                text = message.content.text.lower()
                
                # Extract numbers from the message
                import re
                numbers = [float(n) for n in re.findall(r"[-+]?\d*\.?\d+", text)]
                
                if len(numbers) >= 2:
                    # Determine which operation to perform
                    if "add" in text or "plus" in text or "+" in text:
                        # Call MCP tool to perform calculation
                        result = await self.call_mcp_tool("calc", "add", a=numbers[0], b=numbers[1])
                        return Message(
                            content=TextContent(text=f"The sum of {numbers[0]} and {numbers[1]} is {result}"),
                            role=MessageRole.AGENT,
                            parent_message_id=message.message_id,
                            conversation_id=message.conversation_id
                        )
                    elif "subtract" in text or "minus" in text or "-" in text:
                        result = await self.call_mcp_tool("calc", "subtract", a=numbers[0], b=numbers[1])
                        return Message(
                            content=TextContent(text=f"The difference between {numbers[0]} and {numbers[1]} is {result}"),
                            role=MessageRole.AGENT,
                            parent_message_id=message.message_id,
                            conversation_id=message.conversation_id
                        )
                    # Add other operations...
            
            # Default response
            return Message(
                content=TextContent(
                    text="I'm a calculator agent. You can ask me to add, subtract, multiply, or divide numbers."
                ),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )
        except Exception as e:
            # Handle errors
            return Message(
                content=TextContent(text=f"Error: {str(e)}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )
# Run the agent
if __name__ == "__main__":
    agent = CalculatorAgent()
    run_server(agent, host="0.0.0.0", port=5000)