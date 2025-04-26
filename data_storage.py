"""
Data storage utilities for the Tick Data Fetcher application.
"""
import os
import csv
import logging
import pandas as pd
from datetime import datetime
import pytz
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config.LOG_FILE,
    filemode='a'
)
logger = logging.getLogger('data_storage')

class TickDataStorage:
    """
    Handles storage of tick data in CSV files.
    """
    def __init__(self):
        self.base_dir = config.BASE_DATA_DIR
        
    def get_file_path(self, symbol, date_str=None):
        """
        Get the file path for storing tick data.
        
        Args:
            symbol (str): Symbol name (e.g., "R_10")
            date_str (str, optional): Date string in YYYY-MM-DD format. 
                                     Defaults to current UTC date.
        
        Returns:
            str: Full path to the CSV file
        """
        if date_str is None:
            date_str = config.get_current_date_str()
            
        return os.path.join(self.base_dir, symbol, f"{date_str}.csv")
    
    def save_ticks(self, symbol, ticks_data):
        """
        Save tick data to a CSV file.
        
        Args:
            symbol (str): Symbol name (e.g., "R_10")
            ticks_data (dict): Tick data from Deriv API
            
        Returns:
            tuple: (success, last_timestamp)
        """
        try:
            if not ticks_data or 'history' not in ticks_data or not ticks_data['history']['times']:
                logger.warning(f"No tick data to save for {symbol}")
                return False, None
                
            # Extract tick data
            times = ticks_data['history']['times']
            prices = ticks_data['history']['prices']
            
            if len(times) != len(prices):
                logger.error(f"Mismatched data lengths: {len(times)} times vs {len(prices)} prices")
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
                logger.warning(f"No data to save for {symbol}")
                return False, None
                
            # Get file path based on the date of the first tick
            first_tick_date = datetime.fromtimestamp(int(times[0]), pytz.UTC).strftime("%Y-%m-%d")
            file_path = self.get_file_path(symbol, first_tick_date)
            
            # Check if file exists to determine if we need to write headers
            file_exists = os.path.isfile(file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save data to CSV
            with open(file_path, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['epoch', 'symbol', 'price'])
                if not file_exists:
                    writer.writeheader()
                writer.writerows(data)
                
            logger.info(f"Saved {len(data)} ticks for {symbol} to {file_path}")
            
            # Return the timestamp of the last tick for incremental fetching
            return True, times[-1]
            
        except Exception as e:
            logger.error(f"Error saving tick data for {symbol}: {str(e)}")
            return False, None
    
    def get_last_timestamp(self, symbol):
        """
        Get the timestamp of the last tick for a symbol.
        
        Args:
            symbol (str): Symbol name (e.g., "R_10")
            
        Returns:
            int: Timestamp of the last tick, or None if no data found
        """
        try:
            # Get current date file
            current_date = config.get_current_date_str()
            file_path = self.get_file_path(symbol, current_date)
            
            if not os.path.isfile(file_path):
                # Check previous day's file
                yesterday = (datetime.now(pytz.UTC) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
                file_path = self.get_file_path(symbol, yesterday)
                
                if not os.path.isfile(file_path):
                    logger.info(f"No existing data file found for {symbol}")
                    return None
            
            # Read the last line of the CSV file
            with open(file_path, 'r') as f:
                # Skip header
                next(f)
                # Read all lines and get the last one
                lines = f.readlines()
                
            if not lines:
                logger.warning(f"File exists but is empty: {file_path}")
                return None
                
            last_line = lines[-1].strip()
            if not last_line:
                logger.warning(f"Last line is empty in file: {file_path}")
                return None
                
            # Parse the last line to get the timestamp
            epoch = last_line.split(',')[0]
            
            logger.info(f"Last timestamp for {symbol}: {epoch}")
            return int(epoch)
            
        except Exception as e:
            logger.error(f"Error getting last timestamp for {symbol}: {str(e)}")
            return None
