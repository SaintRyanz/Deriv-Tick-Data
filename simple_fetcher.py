"""
Simple script to fetch tick data from Deriv API.
"""
import os
import json
import time
import csv
import websocket
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API URL
DERIV_API_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

# Symbols to fetch
SYMBOLS = ["R_10", "R_75", "R_100"]

def ensure_dir(directory):
    """Ensure directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def connect_to_api():
    """Connect to Deriv API."""
    try:
        ws = websocket.create_connection(DERIV_API_URL)
        print("Connected to Deriv API")
        
        # Get API token
        api_token = os.getenv("DERIV_API_TOKEN")
        if not api_token or api_token.strip() == "":
            print("API token is empty or not set")
            return None
            
        # Authenticate with API token
        auth_request = {
            "authorize": api_token
        }
        ws.send(json.dumps(auth_request))
        response = json.loads(ws.recv())
        
        if "error" in response:
            print(f"Authentication failed: {response['error']['message']}")
            return None
            
        print("Successfully authenticated with Deriv API")
        return ws
        
    except Exception as e:
        print(f"Connection error: {str(e)}")
        return None

def fetch_ticks(ws, symbol, count=5000, start_time=None):
    """Fetch tick history for a symbol."""
    try:
        request = {
            "ticks_history": symbol,
            "style": "ticks",
            "end": "latest",
            "count": count
        }
        
        # Add start time if provided
        if start_time:
            request["start"] = start_time
        
        ws.send(json.dumps(request))
        response = json.loads(ws.recv())
        
        if "error" in response:
            print(f"API error: {response['error']['message']}")
            return None
        
        return response
        
    except Exception as e:
        print(f"Error fetching ticks: {str(e)}")
        return None

def get_last_timestamp(symbol):
    """Get the timestamp of the last tick for a symbol."""
    try:
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_path = f"data/{symbol}/{current_date}.csv"
        
        if not os.path.isfile(file_path):
            # Check previous day's file
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            file_path = f"data/{symbol}/{yesterday}.csv"
            
            if not os.path.isfile(file_path):
                print(f"No existing data file found for {symbol}")
                return None
        
        # Read the last line of the CSV file
        with open(file_path, 'r') as f:
            # Skip header
            next(f)
            # Read all lines and get the last one
            lines = f.readlines()
            
        if not lines:
            print(f"File exists but is empty: {file_path}")
            return None
            
        last_line = lines[-1].strip()
        if not last_line:
            print(f"Last line is empty in file: {file_path}")
            return None
            
        # Parse the last line to get the timestamp
        epoch = last_line.split(',')[0]
        
        print(f"Last timestamp for {symbol}: {epoch}")
        return int(epoch)
        
    except Exception as e:
        print(f"Error getting last timestamp for {symbol}: {str(e)}")
        return None

def save_ticks(symbol, ticks_data):
    """Save tick data to a CSV file."""
    try:
        if not ticks_data or 'history' not in ticks_data or not ticks_data['history']['times']:
            print(f"No tick data to save for {symbol}")
            return False, None
            
        # Extract tick data
        times = ticks_data['history']['times']
        prices = ticks_data['history']['prices']
        
        if len(times) != len(prices):
            print(f"Mismatched data lengths: {len(times)} times vs {len(prices)} prices")
            return False, None
            
        # Prepare data for CSV
        data = []
        for i in range(len(times)):
            data.append({
                'epoch': times[i],
                'symbol': symbol,
                'price': prices[i]
            })
            
        if not data:
            print(f"No data to save for {symbol}")
            return False, None
            
        # Get file path based on the date of the first tick
        first_tick_date = datetime.fromtimestamp(int(times[0])).strftime("%Y-%m-%d")
        file_path = f"data/{symbol}/{first_tick_date}.csv"
        
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.isfile(file_path)
        
        # Create directory if it doesn't exist
        ensure_dir(os.path.dirname(file_path))
        
        # Save data to CSV
        with open(file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['epoch', 'symbol', 'price'])
            if not file_exists:
                writer.writeheader()
            writer.writerows(data)
            
        print(f"Saved {len(data)} ticks for {symbol} to {file_path}")
        
        # Return the timestamp of the last tick for incremental fetching
        return True, times[-1]
        
    except Exception as e:
        print(f"Error saving tick data for {symbol}: {str(e)}")
        return False, None

def fetch_symbol_data(ws, symbol):
    """Fetch tick data for a single symbol."""
    try:
        print(f"Fetching data for {symbol}")
        
        # Get the timestamp of the last tick
        last_timestamp = get_last_timestamp(symbol)
        
        # Add 1 second to avoid duplicate ticks
        if last_timestamp:
            last_timestamp += 1
            print(f"Continuing from timestamp {last_timestamp} for {symbol}")
        
        # Fetch ticks from the API
        ticks_data = fetch_ticks(ws, symbol, count=5000, start_time=last_timestamp)
        
        if not ticks_data or "history" not in ticks_data:
            print(f"Failed to fetch ticks for {symbol}")
            return False
            
        # Check if we got any ticks
        if not ticks_data["history"]["times"]:
            print(f"No new ticks available for {symbol}")
            return True
            
        # Save the ticks to storage
        success, new_last_timestamp = save_ticks(symbol, ticks_data)
        
        if success:
            print(f"Successfully fetched and saved {len(ticks_data['history']['times'])} ticks for {symbol}")
            return True
        else:
            print(f"Failed to save ticks for {symbol}")
            return False
            
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return False

def main():
    """Main function."""
    print("Starting Deriv Tick Data Fetcher")
    
    # Connect to API
    ws = connect_to_api()
    if not ws:
        print("Failed to connect to API")
        return
    
    try:
        # Fetch data for all symbols
        for symbol in SYMBOLS:
            fetch_symbol_data(ws, symbol)
            # Small delay between symbols
            time.sleep(1)
        
        # Disconnect from API
        ws.close()
        print("Disconnected from Deriv API")
        
    except Exception as e:
        print(f"Error during fetch cycle: {str(e)}")
        
        # Ensure API is disconnected
        try:
            ws.close()
        except:
            pass

if __name__ == "__main__":
    main()
