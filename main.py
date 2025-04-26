"""
Main entry point for the Deriv Index Tick Data Fetcher application.
"""
import os
import logging
import signal
import sys
import time
from dotenv import load_dotenv
import config
from scheduler import TickDataScheduler

# Set up logging to console and file
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('main')

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

def handle_exit(signum, frame):
    """Handle exit signals gracefully."""
    logger.info("Received exit signal. Shutting down...")
    if scheduler and scheduler.is_running():
        scheduler.stop()
    sys.exit(0)

def main():
    """Main application entry point."""
    logger.info("Starting Deriv Index Tick Data Fetcher")
    
    # Check if API token is set
    if not check_api_token():
        return
    
    # Create scheduler
    global scheduler
    scheduler = TickDataScheduler()
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    try:
        # Print application info
        print("\n=== Deriv Index Tick Data Fetcher ===")
        print(f"Fetching data for symbols: {', '.join(config.SYMBOLS)}")
        print(f"Fetch interval: {config.FETCH_INTERVAL_SECONDS} seconds (~{config.FETCH_INTERVAL_SECONDS/3600:.2f} hours)")
        print(f"Data directory: {config.BASE_DATA_DIR}")
        print(f"Log file: {config.LOG_FILE}")
        print("\nPress Ctrl+C to exit\n")
        
        # Start the scheduler
        scheduler.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        if scheduler.is_running():
            scheduler.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if scheduler and scheduler.is_running():
            scheduler.stop()

if __name__ == "__main__":
    main()
