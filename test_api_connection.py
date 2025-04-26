"""
Test script to verify the Deriv API connection.
"""
import os
import json
import websocket
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()

# Load environment variables
load_dotenv()

# API URL
DERIV_API_URL = "wss://ws.binaryws.com/websockets/v3"

def test_connection():
    """Test connection to Deriv API."""
    print("\n=== Testing Deriv API Connection ===")
    
    # Get API token
    api_token = os.getenv("DERIV_API_TOKEN")
    if not api_token or api_token.strip() == "":
        print("ERROR: API token is empty or not set in .env file")
        return False
    
    print(f"Using API token: {api_token[:4]}...{api_token[-4:]}")
    
    try:
        # Enable websocket debugging
        websocket.enableTrace(True)
        
        print("\nConnecting to Deriv API...")
        ws = websocket.create_connection(
            DERIV_API_URL,
            header=[
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Origin: https://app.deriv.com"
            ]
        )
        print("Connected to WebSocket API")
        
        # Test ping
        print("\nSending ping request...")
        ping_request = {
            "ping": 1
        }
        ws.send(json.dumps(ping_request))
        response = json.loads(ws.recv())
        print(f"Ping response: {response}")
        
        if "pong" in response:
            print("✓ Ping successful")
        else:
            print("✗ Ping failed")
            return False
        
        # Test authorization
        print("\nAuthorizing with API token...")
        auth_request = {
            "authorize": api_token
        }
        ws.send(json.dumps(auth_request))
        response = json.loads(ws.recv())
        print(f"Authorization response: {json.dumps(response, indent=2)}")
        
        if "error" in response:
            print(f"✗ Authorization failed: {response['error']['message']}")
            return False
        else:
            print("✓ Authorization successful")
            
            if "authorize" in response:
                print(f"Account info: {response['authorize'].get('email', 'N/A')}")
                print(f"Balance: {response['authorize'].get('balance', 'N/A')}")
        
        # Test ticks request
        print("\nRequesting tick data for R_10...")
        ticks_request = {
            "ticks": "R_10",
            "subscribe": 1
        }
        ws.send(json.dumps(ticks_request))
        response = json.loads(ws.recv())
        print(f"Ticks response: {json.dumps(response, indent=2)}")
        
        if "error" in response:
            print(f"✗ Ticks request failed: {response['error']['message']}")
        else:
            print("✓ Ticks request successful")
            
            # Unsubscribe
            print("\nUnsubscribing from ticks...")
            forget_request = {
                "forget_all": "ticks"
            }
            ws.send(json.dumps(forget_request))
            response = json.loads(ws.recv())
            print(f"Unsubscribe response: {response}")
        
        # Close connection
        ws.close()
        print("\nConnection closed")
        return True
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        logger.error(f"Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
