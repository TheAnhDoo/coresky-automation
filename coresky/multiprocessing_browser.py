import os
import time
import logging
import sys
import signal
import multiprocessing
import psutil
import math
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import config
import metamask
import coresky
from utils import take_screenshot, close_dialog_if_exists

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - [Process %(process)d]',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('automation_multi.log')
    ]
)

logger = logging.getLogger(__name__)

# Global flag to signal processes to stop
running = multiprocessing.Value('i', 1)

def signal_handler(sig, frame):
    """Handle Ctrl+C by setting the running flag to 0"""
    global running
    logger.info("Stopping all processes...")
    with running.get_lock():
        running.value = 0
    
def initialize_browser(process_id):
    """
    Initialize Chrome browser with MetaMask extension with small window size
    
    Returns:
        WebDriver: Initialized Chrome WebDriver or None if failed
    """
    logger.info(f"[Process {process_id}] Initializing Chrome browser")
    
    try:
        # Check if extensions exist
        if not os.path.exists(config.METAMASK_CRX_PATH):
            logger.error(f"MetaMask extension file not found: {config.METAMASK_CRX_PATH}")
            return None
            
        # Set up Chrome options
        chrome_options = Options()
        
        # Set small window size to reduce memory usage
        chrome_options.add_argument("--window-size=600,300")
        chrome_options.add_argument("--disable-notifications")
        
        # Add options to reduce memory usage and improve compatibility
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-browser-side-navigation")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--headless=new")  # Use new headless mode

        
        # Add MetaMask extension
        chrome_options.add_extension(config.METAMASK_CRX_PATH)
        
        # Set up Chrome service
        if not os.path.exists(config.CHROMEDRIVER_PATH):
            logger.error(f"ChromeDriver not found: {config.CHROMEDRIVER_PATH}")
            return None
            
        service = Service(executable_path=config.CHROMEDRIVER_PATH)
        
        # Initialize the driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set implicit wait time
        driver.implicitly_wait(config.DEFAULT_IMPLICIT_WAIT)
        
        # Close any extra tabs that might have opened with extensions
        if len(driver.window_handles) > 1:
            logger.info(f"Found {len(driver.window_handles)} tabs, closing extras")
            main_handle = driver.window_handles[0]
            for handle in driver.window_handles[1:]:
                driver.switch_to.window(handle)
                driver.close()
            driver.switch_to.window(main_handle)
        
        logger.info(f"[Process {process_id}] Browser initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"[Process {process_id}] Error initializing browser: {e}")
        return None

def run_browser_instance(process_id):
    """
    Run a complete automation cycle in a single browser instance
    
    Args:
        process_id: Unique identifier for this browser process
    """
    logger.info(f"[Process {process_id}] Starting browser instance")
    driver = None
    
    while running.value == 1:
        try:
            # Initialize the browser
            if driver is None:
                driver = initialize_browser(process_id)
                if not driver:
                    logger.error(f"[Process {process_id}] Failed to initialize browser, retrying in 30 seconds")
                    time.sleep(30)
                    continue
            
            # Set up MetaMask wallet
            logger.info(f"[Process {process_id}] Setting up MetaMask wallet")
            metamask_setup_success = metamask.setup_metamask_wallet(driver)
            if not metamask_setup_success:
                logger.error(f"[Process {process_id}] Failed to set up MetaMask wallet, restarting browser")
                driver.quit()
                driver = None
                time.sleep(10)
                continue
            
            # Connect MetaMask to Coresky
            logger.info(f"[Process {process_id}] Connecting MetaMask to Coresky")
            connect_success = metamask.connect_metamask_to_coresky(driver, config.CORESKY_URL)
            if not connect_success:
                logger.error(f"[Process {process_id}] Failed to connect MetaMask to Coresky, restarting browser")
                driver.quit()
                driver = None
                time.sleep(10)
                continue
            
            # Perform Coresky tasks
            logger.info(f"[Process {process_id}] Performing Coresky tasks")
            tasks_success = coresky.perform_all_available_tasks(driver)
            if not tasks_success:
                logger.warning(f"[Process {process_id}] Some Coresky tasks may have failed")
            else:
                logger.info(f"[Process {process_id}] All Coresky tasks completed successfully")
            
            # Clean up and restart a new cycle
            logger.info(f"[Process {process_id}] Cycle completed, restarting browser for a new cycle")
            driver.quit()
            driver = None
            time.sleep(10)  # Brief pause before starting a new cycle
            
        except Exception as e:
            logger.error(f"[Process {process_id}] Error during automation cycle: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
                driver = None
            time.sleep(30)  # Wait longer on error
        
        # Check if we should continue running
        if running.value == 0:
            break
            
    # Clean up
    if driver:
        try:
            driver.quit()
        except:
            pass
    logger.info(f"[Process {process_id}] Process stopped")

def estimate_max_instances():
    """
    Estimate maximum number of Chrome instances based on system resources
    """
    try:
        # Get system information
        mem = psutil.virtual_memory()
        total_mem_gb = mem.total / (1024 * 1024 * 1024)
        available_mem_gb = mem.available / (1024 * 1024 * 1024)
        cpu_count = multiprocessing.cpu_count()
        
        # Calculate max instances based on memory and CPU
        # Assume each Chrome instance needs ~300MB minimum
        max_by_mem = math.floor(available_mem_gb * 0.8 / 0.3)  # Use 80% of available memory
        
        # For CPU, leave 1 core for system and use 80% of remaining
        max_by_cpu = math.floor((cpu_count - 1) * 0.8)
        
        # Take the minimum of the two limits
        max_instances = min(max_by_mem, max_by_cpu)
        max_instances = max(1, min(max_instances, 100))  # Cap between 1 and 100
        
        logger.info(f"System has {total_mem_gb:.2f}GB total RAM, {available_mem_gb:.2f}GB available")
        logger.info(f"System has {cpu_count} CPU threads")
        logger.info(f"Estimated maximum browser instances: {max_instances}")
        
        return 1
    except Exception as e:
        logger.error(f"Error estimating max instances: {e}")
        return 4  # Safe default

def main():
    """
    Main function to start multiple browser instances
    """
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command line arguments
    num_instances = 0
    try:
        for arg in sys.argv[1:]:
            if arg.startswith("--instances="):
                num_instances = int(arg.split("=")[1])
    except Exception as e:
        logger.error(f"Error parsing command line arguments: {e}")
    
    # If not specified, estimate the maximum instances
    if num_instances <= 0:
        num_instances = estimate_max_instances()
    
    logger.info(f"Starting automation with {num_instances} parallel browser instances")
    
    # Create and start processes
    processes = []
    try:
        for i in range(num_instances):
            p = multiprocessing.Process(target=run_browser_instance, args=(i,))
            processes.append(p)
            p.start()
            time.sleep(2)  # Stagger starts to avoid overwhelming the system
            
        # Wait for all processes to complete
        while any(p.is_alive() for p in processes) and running.value == 1:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Automation interrupted by user")
        with running.get_lock():
            running.value = 0
    except Exception as e:
        logger.error(f"Unhandled error in automation: {e}")
        with running.get_lock():
            running.value = 0
    finally:
        # Clean up
        with running.get_lock():
            running.value = 0
            
        # Wait for processes to terminate
        wait_time = 0
        while any(p.is_alive() for p in processes) and wait_time < 30:
            time.sleep(1)
            wait_time += 1
            
        # Force terminate any remaining processes
        for p in processes:
            if p.is_alive():
                logger.info(f"Force terminating process {p.pid}")
                p.terminate()
                
        logger.info("All processes stopped")
        
if __name__ == "__main__":
    main() 