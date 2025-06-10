# from a2a.client import A2AClient, AgentCard
from python_a2a import A2AClient, AgentCard

# 1) Discover Agent 1 by fetching its AgentCard
agent_url = "http://localhost:9000"
card = AgentCard.fetch(f"{agent_url}/.well-known/agent.json")

# 2) Create a client from that card
client = A2AClient.from_agent_card(card)

# 3) Call the 'add' tool
res_add = client.call_method(
    method="add",
    params={"a": 5, "b": 7},
).result()
print("5 + 7 =", res_add)  # → 12

# 4) Call the 'square' tool
res_sq = client.call_method(
    method="square",
    params={"a": 4},
).result()
print("4² =", res_sq)     # → 16
