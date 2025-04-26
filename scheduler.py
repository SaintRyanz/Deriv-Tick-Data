"""
Scheduling functionality for the Tick Data Fetcher application.
"""
import logging
import time
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import config
from data_fetcher import TickDataFetcher

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config.LOG_FILE,
    filemode='a'
)
logger = logging.getLogger('scheduler')

class TickDataScheduler:
    """
    Handles scheduling of tick data fetching.
    """
    def __init__(self):
        self.fetcher = TickDataFetcher()
        self.scheduler = BackgroundScheduler()
        self.running = False
        
    def start(self):
        """
        Start the scheduler.
        """
        if self.running:
            logger.warning("Scheduler is already running")
            return
            
        try:
            # Schedule the fetch job to run at the configured interval
            self.scheduler.add_job(
                self.fetcher.run_fetch_cycle,
                IntervalTrigger(seconds=config.FETCH_INTERVAL_SECONDS),
                id='fetch_job',
                replace_existing=True,
                next_run_time=datetime.now(pytz.UTC)  # Run immediately on start
            )
            
            # Start the scheduler
            self.scheduler.start()
            self.running = True
            
            logger.info(f"Scheduler started. Fetch interval: {config.FETCH_INTERVAL_SECONDS} seconds")
            
            # Calculate and log the next run time
            next_run = datetime.now(pytz.UTC) + timedelta(seconds=config.FETCH_INTERVAL_SECONDS)
            logger.info(f"Next scheduled run: {next_run}")
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
            
    def stop(self):
        """
        Stop the scheduler.
        """
        if not self.running:
            logger.warning("Scheduler is not running")
            return
            
        try:
            self.scheduler.shutdown()
            self.running = False
            logger.info("Scheduler stopped")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
            
    def run_once(self):
        """
        Run a single fetch cycle immediately.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Running manual fetch cycle")
        return self.fetcher.run_fetch_cycle()
        
    def is_running(self):
        """
        Check if the scheduler is running.
        
        Returns:
            bool: True if running, False otherwise
        """
        return self.running
