import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import config
import metamask
from utils import take_screenshot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('metamask_test.log')
    ]
)

logger = logging.getLogger(__name__)

def initialize_browser():
    """Initialize Chrome browser with MetaMask extension"""
    logger.info("Initializing Chrome browser for MetaMask testing")
    
    try:
        # Check if extensions exist
        if not os.path.exists(config.METAMASK_CRX_PATH):
            logger.error(f"MetaMask extension file not found: {config.METAMASK_CRX_PATH}")
            return None
            
        # Set up Chrome options
        chrome_options = Options()
        
        # Add arguments
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        
        # Add MetaMask extension
        chrome_options.add_extension(config.METAMASK_CRX_PATH)
        
        # For debugging
        chrome_options.add_argument("--auto-open-devtools-for-tabs")
        
        # Set up Chrome service
        if os.path.exists(config.CHROMEDRIVER_PATH):
            service = Service(executable_path=config.CHROMEDRIVER_PATH)
        else:
            logger.warning(f"ChromeDriver not found at {config.CHROMEDRIVER_PATH}, using system default")
            service = Service()
        
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

def test_metamask_setup():
    """Test MetaMask wallet setup"""
    driver = None
    try:
        # Initialize browser
        driver = initialize_browser()
        if not driver:
            logger.error("Failed to initialize browser")
            return False
            
        # Take screenshot of initial state
        take_screenshot(driver, "test_metamask_initial")
        
        # Set up MetaMask wallet
        logger.info("Setting up MetaMask wallet")
        setup_success = metamask.setup_metamask_wallet(driver, take_screenshots=True)
        
        if setup_success:
            logger.info("MetaMask wallet setup successful")
            take_screenshot(driver, "test_metamask_success")
            return True
        else:
            logger.error("MetaMask wallet setup failed")
            take_screenshot(driver, "test_metamask_failed")
            return False
    except Exception as e:
        logger.error(f"Error during MetaMask testing: {e}")
        if driver:
            take_screenshot(driver, "test_metamask_error")
        return False
    finally:
        # Keep browser open for manual inspection
        if driver:
            logger.info("Test completed. Browser will remain open for inspection.")
            # Uncomment the following line to close the browser automatically
            # driver.quit()

if __name__ == "__main__":
    # Create screenshots directory if it doesn't exist
    os.makedirs(config.SCREENSHOTS_DIR, exist_ok=True)
    
    logger.info("Starting MetaMask setup test")
    test_result = test_metamask_setup()
    
    if test_result:
        logger.info("MetaMask test completed successfully")
    else:
        logger.error("MetaMask test failed")
        
    logger.info("Test script finished. Browser is kept open for inspection.")
    # The browser will stay open for manual inspection 