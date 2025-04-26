"""
Test script to verify the Deriv API connection using the official approach.
"""
import os
import json
import time
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
DERIV_API_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

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
        # Connect to WebSocket
        print("\nConnecting to Deriv API...")
        ws = websocket.create_connection(DERIV_API_URL)
        print("Connected to WebSocket API")
        
        # Test ping
        print("\nSending ping request...")
        ping_request = {
            "ping": 1
        }
        ws.send(json.dumps(ping_request))
        response = json.loads(ws.recv())
        print(f"Ping response: {response}")
        
        if "ping" in response and response["ping"] == "pong":
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
        
        # Test ticks history request
        print("\nRequesting tick history for R_10...")
        ticks_request = {
            "ticks_history": "R_10",
            "count": 10,
            "end": "latest",
            "style": "ticks"
        }
        ws.send(json.dumps(ticks_request))
        response = json.loads(ws.recv())
        
        if "error" in response:
            print(f"✗ Ticks history request failed: {response['error']['message']}")
            return False
        else:
            print("✓ Ticks history request successful")
            print(f"Received {len(response['history']['prices'])} ticks")
            
            # Print first few ticks
            if 'history' in response and 'times' in response['history'] and 'prices' in response['history']:
                times = response['history']['times']
                prices = response['history']['prices']
                
                print("\nSample tick data:")
                for i in range(min(5, len(times))):
                    print(f"Time: {times[i]}, Price: {prices[i]}")
        
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
