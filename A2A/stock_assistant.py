# pricing_assistant.py
import json
from python_a2a import OllamaA2AServer, OpenAIA2AServer, A2AClient, Message, TextContent, MessageRole, run_server
import os
from dotenv import load_dotenv
# Use OllamaPricingCalculator for Azure pricing
from cloud_price_service.azure_service import OllamaPricingCalculator
import asyncio
# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from python_a2a import A2AClient, Message, TextContent, MessageRole, run_server
import os
from db_config import azure_description_config

async def ollamacalculator(description, price_response):
    # Connect to the server using SSE
   azure_service = OllamaPricingCalculator()
   azure_pricing = await azure_service.calculate_pricing(description, price_response.content.text)
   return azure_pricing

class CloudPriceAssistant(OllamaA2AServer):
    """An AI assistant for cloud pricing information that coordinates specialized agents."""

    def __init__(self, db_agent_endpoint, pricing_agent_endpoint):
        # Initialize the OpenAI-powered agent
        super().__init__(
            api_url="http://localhost:11434",  # Required for Ollama connection
            model="gemma3:27b",
            system_prompt=(
                "You are a helpful assistant that helps users get cloud pricing information. "
            )
        )
        
        # Create clients for connecting to specialized agents
        self.db_client = A2AClient(db_agent_endpoint)
        self.pricing_client = A2AClient(pricing_agent_endpoint)

    def handle_message(self, message):
        """Override to intercept cloud pricing queries."""
        if message.content.type == "text":
            text = message.content.text.lower()
            logger.info(f"Received message: {text}")
            
            # First, use OpenAI to extract the agent name or cloud name
            ollama_response = super().handle_message(Message(
                content=TextContent(
                    text=f"""Identify whether the user query is about agent detail extraction or cloud pricing extraction.
1. If the query is about agent detail extraction, extract and return only the Agent.
2. If the query is about cloud pricing extraction, extract and return only the cloud name from the following options:
AWS Cloud
Azure Cloud
GCP Cloud

If no cloud service is mentioned, return Azure Cloud by default.
Return only the extracted name (Agent, AWS Cloud, Azure Cloud, GCP Cloud), nothing else.

### User Query:
{message.content.text}
"""),
                role=MessageRole.USER
            ))
            logger.info(f"Ollama response: {ollama_response.content.text}")
            query_type = ollama_response.content.text.strip()
            query_type = query_type.strip('"\'.,')
            logger.info(f"Extracted cloud name: {query_type}")

            # Check if this is a cloud pricing query
            if (query_type.lower() in ["aws cloud", "azure cloud", "gcp cloud"]):
                # Process as a cloud pricing query
                logger.info("Processing cloud pricing query.")
                return self._get_cloud_pricing_info(message, query_type)
            # Check if this is an agent detail extraction query
            elif query_type.lower() == "agent":
                # Process as an agent detail extraction query
                logger.info("Processing agent detail extraction query.")
                return self._get_agent_detail_info(message)

        # For all other messages, defer to OpenAI
        return super().handle_message(message)

    def _get_cloud_pricing_info(self, message, cloud_name):
        """Process a cloud pricing information query by coordinating with specialized agents."""
        try:
            # Second, use OpenAI to extract the service name
            ollama_response = super().handle_message(Message(
                content=TextContent(
                    text=f"""Extract the service name from this query: '{message.content.text}'.
from the following options:
1. KF+Ops
2. KF+SDLC
3. KF+Ops+SDLC
4. KF+Modernization
Return ONLY the service name, nothing else.
If no service is mentioned, return KF+Ops."""),
                role=MessageRole.USER
            ))
            logger.info(f"Ollama response: {ollama_response.content.text}")
            service_name = ollama_response.content.text.strip()
            service_name = service_name.strip('"\'.,')
            logger.info(f"Extracted service name: {service_name}")

            # Step 1: Get API filter from DB agent
            db_data = {
                "cloud_name": cloud_name,
                "service_name": service_name
            }
            db_json_str = json.dumps(db_data)
            api_filter_message = Message(
                content=TextContent(text=db_json_str),
                role=MessageRole.USER
            )
            api_filter_response = self.db_client.send_message(api_filter_message)
            logger.info(f"API filter response: {api_filter_response.content.text}")

            # Second, use OpenAI to extract the API filter
            ollama_response = super().handle_message(Message(
                content=TextContent(
                    text=f"""Generate Azure pricing filters using Data syntax and User Query. Follow these rules:
1. Analyze multi-part questions and decompose into service components
2. Use ONLY these attributes for filtering:
    - meterName 
    - serviceFamily
    - productName
    - skuName
    - location
3. Region handling:
    - Explicitly extract region from input when available
    - Default to 'US East' if unspecified
4. Filter construction:
    a. Group service conditions in parentheses using 'or' logic
    b. Combine service group with location using 'and' logic
5. Output ONLY the Data filter string with no additional text like function call or anything.

### Valid Examples:
Input: "AKS pricing in East US for KF+Ops?"
Output: 
(
    (meterName eq 'Standard Uptime SLA') or (serviceFamily eq 'Compute' and meterName eq 'D16as v4')
) and location eq 'US East'

Input: "KF+Ops+SDLC costs for West US?"
Output:
(
    (meterName eq 'Standard Uptime SLA') or 
    (serviceFamily eq 'Compute' and meterName eq 'D16as v4') or
    (skuName eq 'gpt-4-Turbo') or
    (productName eq 'Azure Premium SSD v2' and meterName eq 'Premium LRS Provisioned Capacity') or
    (productName eq 'Premium SSD Managed Disks' and meterName eq 'P20 LRS Disk') or 
    (productName eq 'Application Gateway WAF v2' and meterName eq 'Standard Fixed Cost') or
    (productName eq 'Container Registry' and meterName eq 'Standard Registry Unit') or
    (serviceFamily eq 'Compute' and meterName eq 'D8ads v5')
) and location eq 'US West'

### Critical Constraints:
- NEVER use unvalidated attributes
- ALWAYS wrap OR groups in parentheses
- Maintain case sensitivity (e.g., 'US East' ≠ 'us east')
- Escape special characters where required

### Filter Data:
{api_filter_response.content.text}

### Query:
{message.content.text}
"""),
                role=MessageRole.USER
            ))
            logger.info(f"Ollama response: {ollama_response.content.text}")
            api_filter = ollama_response.content.text.strip()
            logger.info(f"Extracted filter: {api_filter}")

            if not api_filter:
                return Message(
                    content=TextContent(text=f"I couldn't find the API filter for {cloud_name}."),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id
                )

            logger.info(f"Found API filter: {api_filter}")

            # Step 2: Get the cloud price from pricing agent
            pricing_data = {
                "cloud_name": cloud_name,
                "filter": api_filter
            }
            pricing_json_str = json.dumps(pricing_data)
            price_message = Message(
                content=TextContent(text=pricing_json_str),
                role=MessageRole.USER
            )
            price_response = self.pricing_client.send_message(price_message)
            logger.info(f"Price response: {price_response.content.text}")

            if service_name.lower() == "kf+ops":
                # Use the KF+Ops description from the config
                description = azure_description_config.AZURE_CLOUD_KF_OPS_DESCRIPTION
            elif service_name.lower() == "kf+sdlc":
                # Use the KF+SDLC description from the config
                description = azure_description_config.AZURE_CLOUD_KF_SDLC_DESCRIPTION
            elif service_name.lower() == "kf+ops+sdlc":
                # Use the KF+Ops+SDLC description from the config
                description = azure_description_config.AZURE_CLOUD_KF_OPS_SDLC_DESCRIPTION
            elif service_name.lower() == "kf+modernization":
                # Use the KF+Modernization description from the config
                description = azure_description_config.AZURE_CLOUD_KF_MODERNIZATION_DESCRIPTION
            else:
                return Message(
                    content=TextContent(text=f"Currently, I only support KF+Ops, KF+SDLC, KF+Ops+SDLC, and KF+Modernization services."),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id
                )

            ollama_response = super().handle_message(Message(
                content=TextContent(
                    text=f"""Generate Azure pricing description using Description Data and User Query. Follow these rules:
1. Analyze multi-part questions and decompose into service components
2. Output ONLY the Data filter string with no additional text like function call or anything.

### Valid Examples:
Input: "AKS pricing in East US for KF+Ops?"
Output: 
Standard; Cluster management for 1 clusters; 7 D16as v4 (16 vCPUs, 64 GB RAM) (1 year reserved), Linux; 0 managed OS disks – S4 (Benchmarked to run 150 Pods) - Azure Kubernetes Service

Input: "KF+SDLC costs for West US?"
Output: 
Standard; Cluster management for 1 clusters; 3 D32as v4 (32 vCPUs, 64 GB RAM) (1 year reserved), Linux; 0 managed OS disks – S4 - Azure Kubernetes Service
Language Models, Standard (On-Demand), GPT-4-Turbo-128K, 20,000 x 1,000 input tokens, 20,000 x 1,000 output tokens - Azure OpenAI
SSD (Premium) Media tier, LRS Redundancy, Provisioned v1 Billing model, Provisioned capacity – 300 GiB Provisioned storage, 3,100 Provisioned IOPS, 110 MiB/sec Provisioned throughput, One Year Reserved – Monthly payments, Used capacity - 0 GiB Used snapshot storage, 0 GiB Used soft-deleted storage - Azure Files
Web Application Firewall V2 tier, 730 Fixed gateway Hours, 1 compute units and 1,000 persistent connections with 1 mb/s throughput, 10 GB Data transfer - Application Gateway
Standard Tier, 1 registry x 30 days, 0 GB Extra Storage, Container Build - 1 CPUs x 1 Seconds - Inter Region transfer type, 5 GB outbound data transfer from East US to East Asia - Azure Container Registry
1 NC12s v3 (12 vCPUs, 224 GB RAM) x 120 Hours (Pay as you go), Linux,  (Pay as you go); 1 managed disk – S15; Inter Region transfer type, 5 GB outbound data transfer from East US to East Asia - Virtual Machines
1 D8ads v5 (8 vCPUs, 32 GB RAM) (1 year reserved), Linux,  (Pay as you go); 1 managed disk – S20; Inter Region transfer type, 5 GB outbound data transfer from East US to East Asia - Virtual Machines

### Description Data: 
{description}

### Query: 
{message.content.text}
"""),
                role=MessageRole.USER
            ))
            logger.info(f"Ollama response: {ollama_response.content.text}")
            service_description = ollama_response.content.text.strip()
            
            if cloud_name.lower() == "azure cloud":
                # description = "Standard; Cluster management for 1 clusters; 7 D16as v4 (16 vCPUs, 64 GB RAM) (1 year reserved), Linux; 0 managed OS disks - S4 (Benchmarked to run 150 Pods)"
                azure_pricing = asyncio.run(ollamacalculator(service_description, price_response))
                logger.info(f"Azure pricing: {azure_pricing}")
            else:
                return Message(
                    content=TextContent(text=f"Currently, I only support Azure pricing queries."),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id
                )

            if not azure_pricing:
                return Message(
                    content=TextContent(text=f"I couldn't find the Azure pricing for {message.content.text}."),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id
                )

            # Return the combined information
            return Message(
                content=TextContent(
                    text=f"{azure_pricing}"
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

    def _get_agent_detail_info(self, message):
        """Process an agent detail extraction query by coordinating with the DB agent."""
        try:
            # Second, use OpenAI to extract the agent name
            ollama_response = super().handle_message(Message(
                content=TextContent(
                    text=f"""Extract the agent name from this query: '{message.content.text}'.
Return ONLY the agent name, nothing else."""),
                role=MessageRole.USER
            ))
            logger.info(f"Ollama response: {ollama_response.content.text}")
            agent_name = ollama_response.content.text.strip()
            logger.info(f"Extracted agent name: {agent_name}")

            if not agent_name:
                return Message(
                    content=TextContent(text="I couldn't find the agent name in your query."),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id
                )

            # Step 1: Get agent details from DB agent
            db_data = {
                "agent_name": agent_name
            }
            db_json_str = json.dumps(db_data)
            agent_message = Message(
                content=TextContent(text=db_json_str),
                role=MessageRole.USER
            )
            agent_response = self.db_client.send_message(agent_message)
            logger.info(f"Agent response: {agent_response.content.text}")

            if not agent_response.content.text:
                return Message(
                    content=TextContent(text=f"I couldn't find details for the agent '{agent_name}'."),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id
                )

            # Return the agent details
            return Message(
                content=TextContent(
                    text=f"Agent Details: {agent_response.content.text}"
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
    assistant = CloudPriceAssistant(
        db_agent_endpoint="http://127.0.0.1:8082/a2a",  # URL of the DB MCP server
        pricing_agent_endpoint="http://127.0.0.1:8084/a2a"  # URL of the Pricing MCP server
    )
    
    run_server(assistant, port=8081)