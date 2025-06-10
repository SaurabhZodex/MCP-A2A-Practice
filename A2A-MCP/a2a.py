from python_a2a import AgentNetwork, A2AClient, A2AMessage 

# Create a network of agents
network = AgentNetwork(name="calculator_network")

# Add agents in different ways
network.add("add_numbers", "http://localhost:8050")  # From URL
network.add("square_number", "http://localhost:8051")  # From client instance

# Discover agents from a list of URLs
# discovered_count = network.discover_agents([
#     "http://localhost:8050",
#     "http://localhost:8051",
# ])
# print(f"Discovered {discovered_count} new agents")

# List all agents in the network
for agent_info in network.list_agents():
    print(f"Agent: {agent_info['name']}")
    print(f"URL: {agent_info['url']}")
    if 'description' in agent_info:
        print(f"Description: {agent_info['description']}")
    print()

# Create a message using A2AMessage instead of a raw dict
message = A2AMessage(data={"a": 2})  # Check the correct constructor format

agent = network.get_agent("square_number")
response = agent.ask({
    "action": "square",
    "input": {"a": 2}
})
print(f"Response from square_number: {response}")