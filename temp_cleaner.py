import os
import shutil
import time
import logging
from datetime import datetime
import psutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('temp_cleaner.log')
    ]
)

logger = logging.getLogger(__name__)

# Define the exact temp folder path
TEMP_FOLDER = r"C:\Users\dothe\AppData\Local\Temp"

def get_temp_folder_size():
    """Get the size of the temp folder in MB"""
    total_size = 0
    
    for dirpath, dirnames, filenames in os.walk(TEMP_FOLDER):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except (OSError, PermissionError):
                continue
    
    return total_size / (1024 * 1024)  # Convert to MB

def clean_temp_folder():
    """Clean the temp folder, skipping files that can't be deleted"""
    deleted_count = 0
    error_count = 0
    
    logger.info(f"Starting temp folder cleanup at {datetime.now()}")
    logger.info(f"Initial temp folder size: {get_temp_folder_size():.2f} MB")
    
    # First, try to delete files
    for root, dirs, files in os.walk(TEMP_FOLDER, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                os.remove(file_path)
                deleted_count += 1
            except (OSError, PermissionError) as e:
                error_count += 1
                continue
        
        # Then try to delete directories
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                shutil.rmtree(dir_path, ignore_errors=True)
                deleted_count += 1
            except (OSError, PermissionError) as e:
                error_count += 1
                continue
    
    logger.info(f"Cleanup completed. Deleted {deleted_count} items, encountered {error_count} errors")
    logger.info(f"Final temp folder size: {get_temp_folder_size():.2f} MB")

def check_disk_space():
    """Check if disk space is running low"""
    try:
        # Get the drive letter from the temp folder path
        drive = os.path.splitdrive(TEMP_FOLDER)[0]
        
        # Check disk usage on the C: drive
        disk_usage = psutil.disk_usage("C:\\")
        logger.info(f"Current disk usage: {disk_usage.percent}%")
        return disk_usage.percent > 90  # Return True if disk usage is over 90%
    except Exception as e:
        logger.error(f"Error checking disk space: {e}")
        return False

def main():
    logger.info("Temp folder cleaner started")
    logger.info(f"Monitoring temp folder: {TEMP_FOLDER}")
    
    while True:
        try:
            # Check if disk space is running low
            if check_disk_space():
                logger.warning("Disk space is running low, initiating cleanup")
                clean_temp_folder()
            else:
                logger.info("Disk space is adequate, skipping cleanup")
            
            # Wait for 10 minutes before next check
            logger.info("Waiting 10 minutes before next check...")
            time.sleep(600)  # 600 seconds = 10 minutes
            
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            time.sleep(60)  # Wait a minute before retrying if there's an error

if __name__ == "__main__":
    main() 