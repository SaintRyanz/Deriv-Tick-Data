"""
Test script to verify the scheduler functionality with a short interval.
"""
import os
import logging
import time
import sys
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# Import our application modules
from deriv_api import DerivAPI
from data_storage import TickDataStorage
from data_fetcher import TickDataFetcher

# Set up logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('test_scheduler')

# Load environment variables
load_dotenv()

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

def main():
    """Main test function."""
    print("\n=== Deriv Index Tick Data Fetcher - Test Script ===")
    print("This script will fetch data every 60 seconds to verify the scheduler functionality.")
    print("Press Ctrl+C to exit\n")
    
    # Check if API token is set
    if not check_api_token():
        return
    
    # Create fetcher
    fetcher = TickDataFetcher()
    
    # Number of fetch cycles to run
    cycles = 5
    
    try:
        for i in range(1, cycles + 1):
            print(f"\nRunning fetch cycle {i}/{cycles}...")
            print(f"Time: {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC")
            
            # Run a fetch cycle
            success = fetcher.run_fetch_cycle()
            
            if success:
                print("Fetch cycle completed successfully!")
            else:
                print("Fetch cycle completed with errors. Check logs for details.")
            
            # Check data directories for files
            for symbol in ["R_10", "R_75", "R_100"]:
                symbol_dir = os.path.join("data", symbol)
                if os.path.exists(symbol_dir):
                    files = os.listdir(symbol_dir)
                    print(f"Files in {symbol_dir}: {', '.join(files) if files else 'None'}")
            
            if i < cycles:
                # Wait for the next cycle (60 seconds)
                next_run = datetime.now(pytz.UTC) + timedelta(seconds=60)
                print(f"\nWaiting 60 seconds until next fetch cycle...")
                print(f"Next run at: {next_run.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                time.sleep(60)
        
        print("\nTest completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nError: {str(e)}")
    finally:
        # Ensure API is disconnected
        if fetcher.api.connected:
            fetcher.api.disconnect()

if __name__ == "__main__":
    main()
