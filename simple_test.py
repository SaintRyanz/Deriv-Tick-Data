"""
Simple test script to verify the scheduler functionality with a short interval.
This script directly tests the API connection and data fetching.
"""
import os
import logging
import time
import sys
import json
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import websocket

# Set up logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("simple_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('simple_test')

# Load environment variables
load_dotenv()

# Configuration
DERIV_API_URL = "wss://ws.binaryws.com/websockets/v3"
SYMBOLS = ["R_10", "R_75", "R_100"]
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def check_api_token():
    """Check if the API token is set in the environment."""
    token = os.getenv("DERIV_API_TOKEN")
    if not token or token.strip() == "":
        logger.error("API token not found. Please set DERIV_API_TOKEN in .env file")
        print("\nERROR: Deriv API token not found!")
        print("Please create a .env file with your API token:")
        print("DERIV_API_TOKEN=your_api_token_here\n")
        return False
    return True

def connect_to_api():
    """Connect to Deriv API and authenticate."""
    try:
        # Add required headers for websocket connection
        ws = websocket.create_connection(
            DERIV_API_URL,
            header=[
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Origin: https://app.deriv.com"
            ]
        )
        logger.info("Connected to Deriv API")
        
        # Get API token
        api_token = os.getenv("DERIV_API_TOKEN")
        if not api_token or api_token.strip() == "":
            logger.error("API token is empty or not set")
            print("API token is empty or not set. Please check your .env file.")
            ws.close()
            return None
            
        # Authenticate with API token
        auth_request = {
            "authorize": api_token
        }
        ws.send(json.dumps(auth_request))
        response = json.loads(ws.recv())
        
        if "error" in response:
            logger.error(f"Authentication failed: {response['error']['message']}")
            print(f"Authentication failed: {response['error']['message']}")
            ws.close()
            return None
            
        logger.info("Successfully authenticated with Deriv API")
        return ws
        
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return None

def fetch_ticks(ws, symbol, count=100):
    """Fetch tick history for a symbol."""
    try:
        request = {
            "ticks_history": symbol,
            "style": "ticks",
            "end": "latest",
            "count": count
        }
        
        ws.send(json.dumps(request))
        response = json.loads(ws.recv())
        
        if "error" in response:
            logger.error(f"API error: {response['error']['message']}")
            return None
        
        return response
        
    except Exception as e:
        logger.error(f"Error fetching ticks: {str(e)}")
        return None

def save_ticks(symbol, ticks_data):
    """Save tick data to a CSV file."""
    try:
        if not ticks_data or 'history' not in ticks_data or not ticks_data['history']['times']:
            logger.warning(f"No tick data to save for {symbol}")
            return False
            
        # Extract tick data
        times = ticks_data['history']['times']
        prices = ticks_data['history']['prices']
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Create directory if it doesn't exist
        symbol_dir = os.path.join(DATA_DIR, symbol)
        os.makedirs(symbol_dir, exist_ok=True)
        
        # File path
        file_path = os.path.join(symbol_dir, f"{current_date}_test.csv")
        
        # Check if file exists
        file_exists = os.path.isfile(file_path)
        
        # Save data to CSV
        with open(file_path, 'a') as f:
            if not file_exists:
                f.write("epoch,symbol,price\n")
                
            for i in range(len(times)):
                f.write(f"{times[i]},{symbol},{prices[i]}\n")
                
        logger.info(f"Saved {len(times)} ticks for {symbol} to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving tick data for {symbol}: {str(e)}")
        return False

def run_fetch_cycle():
    """Run a fetch cycle for all symbols."""
    print(f"\nRunning fetch cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Connect to API
    ws = connect_to_api()
    if not ws:
        print("Failed to connect to API")
        return False
    
    try:
        success = True
        
        # Fetch and save data for each symbol
        for symbol in SYMBOLS:
            print(f"Fetching data for {symbol}...")
            
            # Fetch ticks
            ticks_data = fetch_ticks(ws, symbol)
            
            if not ticks_data:
                print(f"Failed to fetch ticks for {symbol}")
                success = False
                continue
                
            # Save ticks
            if save_ticks(symbol, ticks_data):
                print(f"Successfully fetched and saved ticks for {symbol}")
            else:
                print(f"Failed to save ticks for {symbol}")
                success = False
        
        # Disconnect from API
        ws.close()
        logger.info("Disconnected from Deriv API")
        
        # Check data directories for files
        for symbol in SYMBOLS:
            symbol_dir = os.path.join(DATA_DIR, symbol)
            if os.path.exists(symbol_dir):
                files = os.listdir(symbol_dir)
                print(f"Files in {symbol_dir}: {', '.join(files) if files else 'None'}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error during fetch cycle: {str(e)}")
        print(f"Error: {str(e)}")
        
        # Ensure API is disconnected
        try:
            ws.close()
        except:
            pass
            
        return False

def main():
    """Main test function."""
    print("\n=== Deriv Index Tick Data Fetcher - Simple Test ===")
    print("This script will fetch data every 60 seconds to verify the functionality.")
    print("Press Ctrl+C to exit\n")
    
    # Check if API token is set
    if not check_api_token():
        return
    
    # Number of cycles to run
    cycles = 5
    
    try:
        for i in range(1, cycles + 1):
            print(f"\nRunning cycle {i}/{cycles}...")
            
            # Run a fetch cycle
            success = run_fetch_cycle()
            
            if success:
                print("Cycle completed successfully!")
            else:
                print("Cycle completed with errors. Check logs for details.")
            
            if i < cycles:
                # Wait for the next cycle (60 seconds)
                next_run = datetime.now() + timedelta(seconds=60)
                print(f"\nWaiting 60 seconds until next cycle...")
                print(f"Next run at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(60)
        
        print("\nTest completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
