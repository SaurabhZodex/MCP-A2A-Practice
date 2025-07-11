import time
from flask import Flask, request, jsonify
from python_a2a import A2AClient, Message, TextContent, MessageRole
import os
# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
a2a_client = None

def initialize_client():
    global a2a_client
    endpoint = os.getenv("A2A_ENDPOINT", "http://localhost:8081/a2a")
    timeout = 600
    a2a_client = A2AClient(endpoint, timeout=timeout)

@app.before_request
def setup_client():
    initialize_client()

@app.route('/ip-infra-costing/query', methods=['POST'])
def handle_query():
    start_time = time.time()
    # Authentication
    auth_token = request.headers.get('Authorization')
    if not validate_token(auth_token):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Input validation
    data = request.json
    user_query = data.get('query')
    logger.info(f"Received query: {user_query}")
    if not user_query:
        return jsonify({"error": "Missing 'query' in request body"}), 400
    
    # Process query
    try:
        message = Message(
            content=TextContent(text=user_query),
            role=MessageRole.USER
        )
        response = a2a_client.send_message(message)
        logger.info(f"Response received: {response.content.text}")
        
        if response.content.type != "text":
            logger.info(f"Query processing time: {time.time() - start_time} seconds")
            return jsonify({"error": "Non-text response received"}), 500
        
        logger.info(f"Query processing time: {time.time() - start_time} seconds")
        
        return jsonify({
            "response": response.content.text,
            "query": user_query
        })
    except Exception as e:
        logger.info(f"Query processing time: {time.time() - start_time} seconds")
        return jsonify({"error": str(e)}), 500

def validate_token(token):
    """Validate bearer token against environment secret"""
    expected_token = os.getenv("API_TOKEN")
    if not expected_token:
        raise EnvironmentError("API_TOKEN not configured")
    return token == f"Bearer {expected_token}"

if __name__ == '__main__':
    expected_token = os.getenv("API_TOKEN")
    logger.info(f"Expected token: {expected_token}")
    initialize_client()
    app.run(host='0.0.0.0', port=8080)