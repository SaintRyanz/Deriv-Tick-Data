"""
Main data fetching logic for the Tick Data Fetcher application.
"""
import logging
import time
from datetime import datetime
import pytz
import config
from deriv_api import DerivAPI
from data_storage import TickDataStorage

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config.LOG_FILE,
    filemode='a'
)
logger = logging.getLogger('data_fetcher')

class TickDataFetcher:
    """
    Handles fetching tick data from Deriv API and storing it.
    """
    def __init__(self):
        self.api = DerivAPI()
        self.storage = TickDataStorage()
        self.symbols = config.SYMBOLS
        
    def fetch_symbol_data(self, symbol):
        """
        Fetch tick data for a single symbol.
        
        Args:
            symbol (str): Symbol to fetch data for (e.g., "R_10")
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Fetching data for {symbol}")
            
            # Get the timestamp of the last tick
            last_timestamp = self.storage.get_last_timestamp(symbol)
            
            # Add 1 second to avoid duplicate ticks
            if last_timestamp:
                last_timestamp += 1
                logger.info(f"Continuing from timestamp {last_timestamp} for {symbol}")
            
            # Fetch ticks from the API
            ticks_data = self.api.get_ticks(symbol, count=config.TICKS_PER_FETCH, start_time=last_timestamp)
            
            if not ticks_data or "history" not in ticks_data:
                logger.error(f"Failed to fetch ticks for {symbol}")
                return False
                
            # Check if we got any ticks
            if not ticks_data["history"]["times"]:
                logger.info(f"No new ticks available for {symbol}")
                return True
                
            # Save the ticks to storage
            success, new_last_timestamp = self.storage.save_ticks(symbol, ticks_data)
            
            if success:
                logger.info(f"Successfully fetched and saved {len(ticks_data['history']['times'])} ticks for {symbol}")
                
                # Log the time range of the fetched data
                first_time = datetime.fromtimestamp(int(ticks_data['history']['times'][0]), pytz.UTC)
                last_time = datetime.fromtimestamp(int(ticks_data['history']['times'][-1]), pytz.UTC)
                logger.info(f"Time range for {symbol}: {first_time} to {last_time}")
                
                return True
            else:
                logger.error(f"Failed to save ticks for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return False
            
    def fetch_all_symbols(self):
        """
        Fetch tick data for all configured symbols.
        
        Returns:
            dict: Results for each symbol (success/failure)
        """
        results = {}
        
        for symbol in self.symbols:
            try:
                success = self.fetch_symbol_data(symbol)
                results[symbol] = success
                
                # Small delay between symbols to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Unexpected error fetching {symbol}: {str(e)}")
                results[symbol] = False
                
        return results
        
    def run_fetch_cycle(self):
        """
        Run a complete fetch cycle for all symbols.
        
        Returns:
            bool: True if all symbols were fetched successfully, False otherwise
        """
        logger.info("Starting fetch cycle")
        
        try:
            # Connect to the API
            if not self.api.connected:
                if not self.api.connect():
                    logger.error("Failed to connect to API")
                    return False
            
            # Fetch data for all symbols
            results = self.fetch_all_symbols()
            
            # Disconnect from the API
            self.api.disconnect()
            
            # Check if all symbols were fetched successfully
            all_success = all(results.values())
            
            if all_success:
                logger.info("Fetch cycle completed successfully")
            else:
                failed_symbols = [symbol for symbol, success in results.items() if not success]
                logger.warning(f"Fetch cycle completed with errors for symbols: {', '.join(failed_symbols)}")
                
            return all_success
            
        except Exception as e:
            logger.error(f"Error during fetch cycle: {str(e)}")
            
            # Ensure API is disconnected
            self.api.disconnect()
            
            return False
