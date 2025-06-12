# # Import required libraries
# from python_a2a.mcp import text_response
# from mcp.server.fastmcp import FastMCP

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# # Create a new MCP server
# calculator_mcp = FastMCP(
#     name="Calculator MCP",
#     version="1.0.0",
#     description="Provides mathematical calculation functions",
#     host="0.0.0.0",  # only used for SSE transport (localhost)
#     port=8050,  # only used for SSE transport (set this to any port)
# )

# # Define tools using simple decorators with type hints
# @calculator_mcp.tool()
# def add(a: float, b: float) -> float:
#     """Add two numbers together."""
#     logger.info(f"Adding {a} and {b}")
#     return a + b

# @calculator_mcp.tool()
# def subtract(a: float, b: float) -> float:
#     """Subtract b from a."""
#     logger.info(f"Subtracting {b} from {a}")
#     return a - b

# @calculator_mcp.tool()
# def multiply(a: float, b: float) -> float:
#     """Multiply two numbers together."""
#     logger.info(f"Multiplying {a} and {b}")
#     return a * b

# @calculator_mcp.tool()
# def divide(a: float, b: float) -> float:
#     """Divide a by b."""
#     logger.info(f"Dividing {a} by {b}")
#     if b == 0:
#         return text_response("Cannot divide by zero")
#     return a / b

# # Example manual testing (optional)
# logger.info("Testing add function: %s", add(5, 3))
# logger.info("Testing subtract function: %s", subtract(10, 4))
# logger.info("Testing multiply function: %s", multiply(6, 7))
# logger.info("Testing divide function: %s", divide(20, 5))
# logger.info("Testing divide by zero: %s", divide(10, 0))


# # Start the MCP server
# logger.info("Calculator MCP server is running on http://0.0.0.0:8050")
# calculator_mcp.run(transport="sse")


# Import all required libraries
from python_a2a.mcp import FastMCP, text_response
import threading
import requests
import re
import yfinance as yf

# YFinance MCP Server for stock price data
yfinance_mcp = FastMCP(
    name="YFinance MCP",
    version="1.0.0",
    description="Stock market data tools"
)

@yfinance_mcp.tool()
def get_stock_price(ticker: str) -> dict:
    """Get current stock price for a given ticker symbol."""
    try:
        # Get stock data
        logger.info(f"Fetching stock data for ticker: {ticker}")
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        
        if data.empty:
            return {"error": f"No data found for ticker {ticker}"}
        
        # Extract the price
        price = data['Close'].iloc[-1]
        
        return {
            "ticker": ticker,
            "price": price,
            "currency": "USD",
            "timestamp": data.index[-1].strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {"error": f"Error fetching stock data: {str(e)}"}


# Test the YFinance stock price lookup
logger.info("\nTesting stock price lookup:")
tickers = ["AAPL", "MSFT", "AMZN"]
for ticker in tickers:
    price_data = get_stock_price(ticker)
    logger.info(f"{ticker} price data: {price_data}")

# For Jupyter Notebook, use threads to run both servers non-blocking
logger.info("YFinance MCP server is running on http://0.0.0.0:5002")
yfinance_mcp.run(host="0.0.0.0", port=5002)
