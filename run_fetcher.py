"""
Run script for the Deriv Index Tick Data Fetcher with a specified interval.
This script allows you to run the fetcher with a custom interval for testing.
"""
import os
import logging
import time
import sys
import argparse
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# Import our application modules
import config
from scheduler import TickDataScheduler

# Set up logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("run_fetcher.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('run_fetcher')

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
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run Deriv Index Tick Data Fetcher with a custom interval')
    parser.add_argument('--interval', type=int, default=config.FETCH_INTERVAL_SECONDS,
                        help=f'Fetch interval in seconds (default: {config.FETCH_INTERVAL_SECONDS})')
    parser.add_argument('--cycles', type=int, default=0,
                        help='Number of cycles to run (0 for unlimited, default: 0)')
    args = parser.parse_args()
    
    # Override the fetch interval if specified
    if args.interval != config.FETCH_INTERVAL_SECONDS:
        config.FETCH_INTERVAL_SECONDS = args.interval
        print(f"Using custom fetch interval: {config.FETCH_INTERVAL_SECONDS} seconds")
    
    print("\n=== Deriv Index Tick Data Fetcher ===")
    print(f"API URL: {config.DERIV_API_URL}")
    print(f"Fetching data for symbols: {', '.join(config.SYMBOLS)}")
    print(f"Fetch interval: {config.FETCH_INTERVAL_SECONDS} seconds (~{config.FETCH_INTERVAL_SECONDS/3600:.2f} hours)")
    print(f"Data directory: {config.BASE_DATA_DIR}")
    print(f"Log file: {config.LOG_FILE}")
    
    if args.cycles > 0:
        print(f"Running for {args.cycles} cycles")
    else:
        print("Running continuously (unlimited cycles)")
    
    print("\nPress Ctrl+C to exit\n")
    
    # Check if API token is set
    if not check_api_token():
        return
    
    # Create and start scheduler
    scheduler = TickDataScheduler()
    scheduler.start()
    
    try:
        # If cycles is specified, run for that many cycles
        if args.cycles > 0:
            # Calculate total runtime
            total_runtime = args.cycles * config.FETCH_INTERVAL_SECONDS
            print(f"Estimated runtime: {timedelta(seconds=total_runtime)}")
            
            # Wait for the specified number of cycles
            start_time = time.time()
            while time.time() - start_time < total_runtime:
                time.sleep(1)
                
            print(f"\nCompleted {args.cycles} cycles")
            scheduler.stop()
        else:
            # Run indefinitely
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down...")
        scheduler.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nError: {str(e)}")
        if scheduler.is_running():
            scheduler.stop()

if __name__ == "__main__":
    main()
