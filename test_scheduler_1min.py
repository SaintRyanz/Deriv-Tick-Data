"""
Test script to verify the scheduler functionality with a 1-minute interval.
This script uses the updated API configuration.
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

# Override the fetch interval for testing
config.FETCH_INTERVAL_SECONDS = 60  # 1 minute for testing

# Set up logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_scheduler_1min.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('test_scheduler')

# Load environment variables
load_dotenv()

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
        next_run = datetime.now() + timedelta(seconds=config.FETCH_INTERVAL_SECONDS)
        logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"Error during fetch cycle: {str(e)}")
        print(f"Error: {str(e)}")

def main():
    """Main test function."""
    print("\n=== Deriv Index Tick Data Fetcher - Test Scheduler (1-minute interval) ===")
    print("This script will fetch data every 1 minute to verify the scheduler functionality.")
    print(f"API URL: {config.DERIV_API_URL}")
    print(f"Symbols: {', '.join(config.SYMBOLS)}")
    print("Press Ctrl+C to exit\n")
    
    # Create scheduler
    scheduler = BackgroundScheduler()
    
    try:
        # Schedule the fetch job to run every 1 minute
        scheduler.add_job(
            run_fetch_cycle,
            IntervalTrigger(seconds=config.FETCH_INTERVAL_SECONDS),
            id='test_fetch_job',
            replace_existing=True,
            next_run_time=datetime.now()  # Run immediately
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info(f"Scheduler started with {config.FETCH_INTERVAL_SECONDS}-second interval")
        print(f"Scheduler started with {config.FETCH_INTERVAL_SECONDS}-second interval")
        
        # Keep the main thread alive for a limited time (5 cycles)
        max_runtime = config.FETCH_INTERVAL_SECONDS * 5  # 5 cycles
        start_time = time.time()
        
        while time.time() - start_time < max_runtime:
            time.sleep(1)
            
        print(f"\nTest completed after {max_runtime} seconds (5 cycles)")
        scheduler.shutdown()
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        print("\nTest interrupted by user.")
        if scheduler.running:
            scheduler.shutdown()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nError: {str(e)}")
        if scheduler.running:
            scheduler.shutdown()

if __name__ == "__main__":
    main()
