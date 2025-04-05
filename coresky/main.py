import os
import time
import logging
import sys
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('automation.log')
    ]
)

logger = logging.getLogger(__name__)

def initialize_browser():
    """
    Initialize Chrome browser with MetaMask extension
    
    Returns:
        WebDriver: Initialized Chrome WebDriver or None if failed
    """
    logger.info("Initializing Chrome browser")
    
    try:
        # Check if extensions exist
        if not os.path.exists(config.METAMASK_CRX_PATH):
            logger.error(f"MetaMask extension file not found: {config.METAMASK_CRX_PATH}")
            return None
            
        # Set up Chrome options
        chrome_options = Options()
        
        # Add arguments
        chrome_options.add_argument("--start-maximized")  # Start maximized
        chrome_options.add_argument("--disable-notifications")  # Disable notifications
        
        # Add extensions
        chrome_options.add_extension(config.METAMASK_CRX_PATH)
        
        # Add SelectorsHub if it exists (optional but helpful for debugging)
        if os.path.exists(config.SELECTORSHUB_CRX_PATH):
            chrome_options.add_extension(config.SELECTORSHUB_CRX_PATH)
            
        # For development/debugging
        if config.DEVELOPMENT_MODE:
            chrome_options.add_argument("--auto-open-devtools-for-tabs")
        
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
        
        logger.info("Browser initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Error initializing browser: {e}")
        return None

def run_full_cycle():
    """
    Run a complete automation cycle
    
    Returns:
        bool: Whether the cycle completed successfully
    """
    driver = None
    try:
        # Initialize the browser
        driver = initialize_browser()
        if not driver:
            logger.error("Failed to initialize browser")
            return False
            
        # Take screenshot of initial browser state
        take_screenshot(driver, "initial_browser")
        
        # Set up MetaMask wallet
        logger.info("Setting up MetaMask wallet")
        metamask_setup_success = metamask.setup_metamask_wallet(driver)
        if not metamask_setup_success:
            logger.error("Failed to set up MetaMask wallet")
            take_screenshot(driver, "metamask_setup_failed")
            return False
            
        take_screenshot(driver, "metamask_setup_complete")
        time.sleep(2)
        # Connect MetaMask to Coresky
        logger.info("Connecting MetaMask to Coresky")
        connect_success = metamask.connect_metamask_to_coresky(driver, config.CORESKY_URL)
        if not connect_success:
            logger.error("Failed to connect MetaMask to Coresky")
            take_screenshot(driver, "metamask_connect_failed")
            return False
            
        take_screenshot(driver, "metamask_connected")
        
        # Perform Coresky tasks
        logger.info("Performing Coresky tasks")
        tasks_success = coresky.perform_all_available_tasks(driver)
        if not tasks_success:
            logger.warning("Some Coresky tasks may have failed")
            take_screenshot(driver, "coresky_tasks_issues")
        else:
            logger.info("All Coresky tasks completed successfully")
            take_screenshot(driver, "coresky_tasks_complete")
        
        # Uninstall MetaMask extension
        logger.info("Cycle completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error during automation cycle: {e}")
        if driver:
            take_screenshot(driver, "error_occurred")
        return False
    finally:
        # Clean up the browser
        if driver and not config.KEEP_BROWSER_OPEN:
            logger.info("Closing browser")
            driver.quit()

def run_multiple_cycles(count=1):
    """
    Run multiple automation cycles
    
    Args:
        count: Number of cycles to run
        
    Returns:
        tuple: (successful_cycles, total_cycles)
    """
    successful_cycles = 0
    
    for i in range(count):
        logger.info(f"Starting cycle {i+1}/{count}")
        
        success = run_full_cycle()
        if success:
            successful_cycles += 1
            logger.info(f"Cycle {i+1} completed successfully")
        else:
            logger.error(f"Cycle {i+1} failed")
            
        # If more cycles to go, add delay between them
        if i < count - 1:
            delay_seconds = config.DELAY_BETWEEN_CYCLES
            logger.info(f"Waiting {delay_seconds} seconds before next cycle")
            time.sleep(delay_seconds)
    
    return successful_cycles, count

if __name__ == "__main__":
    # Parse command line arguments
    cycle_count = 1
    debug_mode = False
    
    try:
        for arg in sys.argv[1:]:
            if arg.startswith("--cycles="):
                cycle_count = int(arg.split("=")[1])
            elif arg == "--debug":
                debug_mode = True
                logging.getLogger().setLevel(logging.DEBUG)
                logger.debug("Debug mode enabled")
    except Exception as e:
        logger.error(f"Error parsing command line arguments: {e}")
    
    logger.info(f"Starting automation with {cycle_count} cycles")
    
    try:
        successful, total = run_multiple_cycles(cycle_count)
        logger.info(f"Automation completed: {successful}/{total} cycles successful")
    except KeyboardInterrupt:
        logger.info("Automation interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled error in automation: {e}")
        
    logger.info("Automation script finished") 