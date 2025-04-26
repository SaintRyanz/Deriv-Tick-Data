"""
Script to sync data from GitHub repository to local machine.
This script pulls the latest data collected by the GitHub Actions workflow.
"""
import os
import sys
import logging
import subprocess
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sync.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

def sync_from_github():
    """Sync data from GitHub repository."""
    logger.info("Starting sync from GitHub")
    print(f"\nSyncing data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Check if we're in a git repository
        if not os.path.exists(".git"):
            logger.error("Not a git repository. Please run this script from the root of your repository.")
            print("ERROR: Not a git repository. Please run this script from the root of your repository.")
            return False
        
        # Fetch the latest changes
        print("Fetching latest changes from GitHub...")
        result = subprocess.run(["git", "fetch", "origin"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Git fetch failed: {result.stderr}")
            print(f"ERROR: Git fetch failed: {result.stderr}")
            return False
        
        # Check if there are changes to pull
        result = subprocess.run(["git", "rev-list", "--count", "HEAD..origin/main"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Git rev-list failed: {result.stderr}")
            print(f"ERROR: Git rev-list failed: {result.stderr}")
            return False
        
        commit_count = int(result.stdout.strip())
        if commit_count == 0:
            logger.info("No new data to sync. Already up to date.")
            print("No new data to sync. Already up to date.")
            return True
        
        # Pull the latest changes
        print(f"Pulling {commit_count} new commits with data updates...")
        result = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Git pull failed: {result.stderr}")
            print(f"ERROR: Git pull failed: {result.stderr}")
            return False
        
        logger.info(f"Successfully synced data from GitHub ({commit_count} new commits)")
        print(f"Successfully synced data from GitHub ({commit_count} new commits)")
        
        # Check data directory for updates
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        if os.path.exists(data_dir):
            symbols = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
            for symbol in symbols:
                symbol_dir = os.path.join(data_dir, symbol)
                files = os.listdir(symbol_dir)
                print(f"Files for {symbol}: {', '.join(files)}")
                
                # Get latest file info
                if files:
                    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(symbol_dir, f)))
                    file_path = os.path.join(symbol_dir, latest_file)
                    size = os.path.getsize(file_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"Latest file: {latest_file} (Size: {size} bytes, Modified: {modified})")
        
        return True
        
    except Exception as e:
        logger.error(f"Sync failed: {str(e)}")
        print(f"ERROR: Sync failed: {str(e)}")
        return False

if __name__ == "__main__":
    sync_from_github()
    print("\nSync process completed. Check sync.log for details.")
