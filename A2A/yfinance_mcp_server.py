# pricing_mcp_server.py
# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all required libraries
# from python_a2a.mcp import FastMC
import httpx
from mcp.server.fastmcp import FastMCP

# # pricing MCP Server for cloud price data
# pricing_mcp = FastMCP(
#     name="Pricing MCP",
#     version="1.0.0",
#     description="Cloud price lookup capabilities"
# )

# pricing MCP Server for cloud price data
pricing_mcp = FastMCP(
    name="Pricing MCP",
    instructions="Cloud price lookup capabilities",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8085,  # only used for SSE transport (set this to any port)
)

@pricing_mcp.tool()
def get_cloud_price(cloud_name: str, filter: str) -> dict:
    """Get current cloud price for a given filter."""
    try:
        # Get cloud price data
        logger.info(f"Fetching cloud price data for filter: {filter}")
        if cloud_name.lower() == "azure cloud":
            azure_data = AzurePricing().fetch_azure_prices(filter)
            if "Items" not in azure_data:
                return {"error": f"No data found for filter {filter}"}

        return azure_data
    except Exception as e:
        return {"error": f"Error fetching cloud data: {str(e)}"}

class AzurePricing:
    def __init__(self):
        # List of keys to extract
        self.REQUIRED_KEY = {
            "serviceName", "serviceFamily", "meterName", "skuName", "unitOfMeasure",
            "reservationTerm", "productName", "currencyCode", "savingsPlan",
            "armRegionName", "retailPrice", "unitPrice", "type"
        }
        self.AZURE_PRICING_ENDPOINT = "https://prices.azure.com/api/retail/prices"

    # Function to extract only required keys from each item
    def extract_relevant_items(self, items, keys):
        extracted_items = []
        for item in items:
            filtered = {k: item.get(k) for k in keys if k in item}
            extracted_items.append(filtered)
        return extracted_items

    def fetch_azure_prices(self, filter_str: str):
        params = {
            "$filter": filter_str,
            "api-version": "2023-01-01-preview"
        }
        with httpx.Client() as client:
            response = client.get(
                self.AZURE_PRICING_ENDPOINT,
                params=params,
            )
            # Extracted result
            filtered_items = self.extract_relevant_items(response.json()["Items"], self.REQUIRED_KEY)
            # print(json.dumps(filtered_items, indent=2))
        return {"Items": filtered_items}

# Test the pricing cloud price lookup
logger.info("\nTesting cloud price lookup:")
filters = ["""((meterName eq 'Standard Uptime SLA') or (serviceFamily eq 'Compute' and meterName eq 'D16as v4')) and location eq 'US East'"""]
for filter in filters:
    price_data = get_cloud_price("Azure Cloud", filter)
    logger.info(f"{filter} price data: {price_data}")

# For Jupyter Notebook, use threads to run both servers non-blocking
logger.info("Pricing MCP server is running on http://0.0.0.0:8085")
# pricing_mcp.run(host="0.0.0.0", port=5002)
pricing_mcp.run(transport="sse")
