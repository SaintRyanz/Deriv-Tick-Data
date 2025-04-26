"""
Deriv API connection handler for the Tick Data Fetcher application.
"""
import json
import logging
import os
import time
import websocket
from dotenv import load_dotenv
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config.LOG_FILE,
    filemode='a'
)
logger = logging.getLogger('deriv_api')

# Load environment variables
load_dotenv()

class DerivAPI:
    """
    Handles connections and requests to the Deriv WebSocket API.
    """
    def __init__(self):
        self.api_url = config.DERIV_API_URL
        self.api_token = os.getenv("DERIV_API_TOKEN")
        if not self.api_token:
            logger.error("API token not found. Please set DERIV_API_TOKEN in .env file")
            raise ValueError("API token not found. Please set DERIV_API_TOKEN in .env file")
        
        self.ws = None
        self.connected = False
    
    def connect(self):
        """
        Establish connection to Deriv WebSocket API.
        """
        try:
            # Connect to WebSocket API with app_id in the URL
            self.ws = websocket.create_connection(self.api_url)
            self.connected = True
            logger.info("Connected to Deriv API")
            
            # Authenticate with API token
            auth_request = {
                "authorize": self.api_token
            }
            self.ws.send(json.dumps(auth_request))
            response = json.loads(self.ws.recv())
            
            if "error" in response:
                logger.error(f"Authentication failed: {response['error']['message']}")
                self.disconnect()
                raise ConnectionError(f"Authentication failed: {response['error']['message']}")
                
            logger.info("Successfully authenticated with Deriv API")
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self):
        """
        Close the WebSocket connection.
        """
        if self.ws and self.connected:
            self.ws.close()
            self.connected = False
            logger.info("Disconnected from Deriv API")
    
    def get_ticks(self, symbol, count=None, start_time=None):
        """
        Fetch tick history for a symbol.
        
        Args:
            symbol (str): Symbol to fetch ticks for (e.g., "R_10")
            count (int, optional): Number of ticks to fetch. Defaults to None.
            start_time (int, optional): Unix timestamp to fetch ticks from. Defaults to None.
            
        Returns:
            dict: API response containing tick data
        """
        if not self.connected:
            if not self.connect():
                logger.error("Cannot fetch ticks: Not connected to API")
                return None
        
        request = {
            "ticks_history": symbol,
            "style": "ticks",
            "end": "latest",
            "count": count if count else config.TICKS_PER_FETCH,
        }
        
        # Add start time if provided
        if start_time:
            request["start"] = start_time
        
        try:
            for _ in range(config.MAX_RETRIES):
                try:
                    self.ws.send(json.dumps(request))
                    response = json.loads(self.ws.recv())
                    
                    if "error" in response:
                        logger.error(f"API error: {response['error']['message']}")
                        if "TokenError" in response['error']['code']:
                            # Token error, need to reconnect
                            self.connect()
                            continue
                        return None
                    
                    return response
                except websocket.WebSocketConnectionClosedException:
                    logger.warning("Connection closed. Reconnecting...")
                    self.connect()
                except Exception as e:
                    logger.error(f"Error during API request: {str(e)}")
                    time.sleep(config.RETRY_DELAY_SECONDS)
            
            logger.error(f"Failed to fetch ticks after {config.MAX_RETRIES} retries")
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch ticks: {str(e)}")
            return None
            

