"""
Test script to verify the data fetching functionality with a short interval.
This script directly uses the scheduler with a 60-second interval.
"""
import os
import logging
import time
import sys
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Import our application modules
import config
from deriv_api import DerivAPI
from data_storage import TickDataStorage
from data_fetcher import TickDataFetcher

# Set up logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_fetch_cycle.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('test_fetch_cycle')

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

def run_fetch_cycle():
    """Run a fetch cycle and log the results."""
    logger.info("Running fetch cycle")
    print(f"\nRunning fetch cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Create fetcher
        fetcher = TickDataFetcher()
        
        # Run a fetch cycle
        success = fetcher.run_fetch_cycle()
        
        if success:
            logger.info("Fetch cycle completed successfully")
            print("Fetch cycle completed successfully!")
        else:
            logger.warning("Fetch cycle completed with errors")
            print("Fetch cycle completed with errors. Check logs for details.")
            
        # Check data directories for files
        for symbol in config.SYMBOLS:
            symbol_dir = os.path.join(config.BASE_DATA_DIR, symbol)
            if os.path.exists(symbol_dir):
                files = os.listdir(symbol_dir)
                file_info = []
                for file in files:
                    file_path = os.path.join(symbol_dir, file)
                    size = os.path.getsize(file_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    file_info.append(f"{file} (Size: {size} bytes, Modified: {modified})")
                
                logger.info(f"Files in {symbol_dir}: {', '.join(file_info) if files else 'None'}")
                print(f"Files in {symbol_dir}: {', '.join(files) if files else 'None'}")
                
        # Calculate next run time
        next_run = datetime.now() + timedelta(seconds=60)
        logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"Error during fetch cycle: {str(e)}")
        print(f"Error: {str(e)}")

def main():
    """Main test function."""
    print("\n=== Deriv Index Tick Data Fetcher - Test Scheduler ===")
    print("This script will fetch data every 60 seconds to verify the scheduler functionality.")
    print("Press Ctrl+C to exit\n")
    
    # Check if API token is set
    if not check_api_token():
        return
    
    # Create scheduler
    scheduler = BackgroundScheduler()
    
    try:
        # Schedule the fetch job to run every 60 seconds
        scheduler.add_job(
            run_fetch_cycle,
            IntervalTrigger(seconds=60),
            id='test_fetch_job',
            replace_existing=True,
            next_run_time=datetime.now()  # Run immediately
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info("Scheduler started with 60-second interval")
        print("Scheduler started with 60-second interval")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        print("\nTest interrupted by user.")
        scheduler.shutdown()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nError: {str(e)}")
        if scheduler.running:
            scheduler.shutdown()

if __name__ == "__main__":
    main()
