# db_mcp_server.py
# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all required libraries
# from python_a2a.mcp import FastMCP
from db_config import azure_filter_config
from mcp.server.fastmcp import FastMCP

# DB MCP Server for API filter lookup
# db_mcp = FastMCP(
#     name="DB MCP",
#     version="1.0.0",
#     description="Search capabilities for finding API filter"
# )

# DB MCP Server for API filter lookup
db_mcp = FastMCP(
    name="DB MCP",
    instructions="Search capabilities for finding API filter",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8083,  # only used for SSE transport (set this to any port)
)

@db_mcp.tool()
def search_api_filter(cloud_name: str, service_name: str) -> str:
    """Find API filter for a given query."""
    # Implementation details (simplified)
    logger.info(f"Searching for API filter for {cloud_name} and {service_name}")
    # Here you would implement the logic to find the API filter
    if cloud_name.lower() == "azure cloud":
        if service_name.lower() == "kf+ops":
            return azure_filter_config.AZURE_CLOUD_KF_OPS_FILTER
        elif service_name.lower() == "kf+sdlc":
            return azure_filter_config.AZURE_CLOUD_KF_SDLC_FILTER
        elif service_name.lower() == "kf+ops+sdlc":
            return azure_filter_config.AZURE_CLOUD_KF_OPS_SDLC_FILTER
        else:
            return azure_filter_config.AZURE_CLOUD_KF_MODERNIZATION_FILTER        

# Example usage - you can run these in a separate cell to test
# Test the DB API filter search
logger.info("\nTesting API filter search:")
api_filter = search_api_filter("Azure Cloud", "KF+Ops")
logger.info(f"API filter for Azure Cloud: {api_filter}")

# For Jupyter Notebook, use threads to run both servers non-blocking
logger.info("DB MCP server is running on http://0.0.0.0:8083")
# db_mcp.run(transport="fastapi", host="0.0.0.0", port=5001)
db_mcp.run(transport="sse")
