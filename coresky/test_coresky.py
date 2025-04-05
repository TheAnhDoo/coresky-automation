import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import config
import coresky
from utils import take_screenshot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('coresky_test.log')
    ]
)

logger = logging.getLogger(__name__)

def initialize_browser():
    """Initialize Chrome browser for Coresky testing"""
    logger.info("Initializing Chrome browser for Coresky testing")
    
    try:
        # Set up Chrome options
        chrome_options = Options()
        
        # Add arguments
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        
        # Add MetaMask extension if it exists (optional for this test)
        if os.path.exists(config.METAMASK_CRX_PATH):
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
        
        logger.info("Browser initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Error initializing browser: {e}")
        return None

def test_coresky_checkin(driver):
    """Test Coresky check-in functionality"""
    try:
        logger.info("Testing Coresky check-in")
        
        # Navigate directly to Coresky
        driver.get(config.CORESKY_URL)
        time.sleep(config.WAIT_MEDIUM)
        
        take_screenshot(driver, "test_coresky_home")
        
        # Perform check-in
        checkin_success = coresky.perform_coresky_checkin(driver)
        
        if checkin_success:
            logger.info("Check-in test successful")
            take_screenshot(driver, "test_checkin_success")
            return True
        else:
            logger.warning("Check-in test may have failed or was already completed")
            take_screenshot(driver, "test_checkin_result")
            return False
    except Exception as e:
        logger.error(f"Error during check-in test: {e}")
        take_screenshot(driver, "test_checkin_error")
        return False

def test_coresky_voting(driver):
    """Test Coresky meme voting functionality"""
    try:
        logger.info("Testing Coresky meme voting")
        
        # Navigate directly to Coresky tasks page
        driver.get(config.CORESKY_TASKS_URL)
        time.sleep(config.WAIT_MEDIUM)
        
        take_screenshot(driver, "test_coresky_tasks")
        
        # Perform meme voting
        voting_success = coresky.vote_for_meme_project(
            driver, 
            config.MEME_PROJECT_NAME, 
            config.MEME_VOTE_POINTS
        )
        
        if voting_success:
            logger.info("Voting test successful")
            take_screenshot(driver, "test_voting_success")
            return True
        else:
            logger.warning("Voting test may have failed or was already completed")
            take_screenshot(driver, "test_voting_result")
            return False
    except Exception as e:
        logger.error(f"Error during voting test: {e}")
        take_screenshot(driver, "test_voting_error")
        return False

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Configuration
CORESKY_URL = "https://www.coresky.com/"
CORESKY_TASKS_URL = "https://www.coresky.com/tasks-rewards"
MEME_PROJECT_NAME = "CupidAI"
MEME_VOTE_POINTS = "20"

# Safe click function
def safe_click(driver, element, max_attempts=3):
    attempts = 0
    while attempts < max_attempts:
        try:
            # First scroll to make sure element is in view
            try:
                logger.info("Scrolling element into view...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
                time.sleep(0.5)
            except Exception as scroll_error:
                logger.error(f"Error scrolling: {scroll_error}")
            
            logger.info("Attempting direct click...")
            element.click()
            logger.info("Click successful")
            return True
        except ElementClickInterceptedException:
            logger.warning("Click was intercepted, checking for dialog...")
            attempts += 1
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error during click: {e}")
            # Try JavaScript click as a fallback
            try:
                logger.info("Trying JavaScript click...")
                driver.execute_script("arguments[0].click();", element)
                logger.info("JavaScript click successful")
                return True
            except Exception as js_error:
                logger.error(f"JavaScript click also failed: {js_error}")
            attempts += 1
            time.sleep(1)

    logger.error(f"Failed to click after {max_attempts} attempts")
    return False

# Function to perform check-in on Coresky
def perform_coresky_checkin(driver):
    try:
        # Navigate to tasks-rewards page
        logger.info(f"Navigating to tasks-rewards page: {CORESKY_TASKS_URL}")
        driver.get(CORESKY_TASKS_URL)
        time.sleep(5)
        
        # Print page details for debugging
        logger.info(f"Current page title: {driver.title}")
        logger.info(f"Current URL: {driver.current_url}")
        
        # Try to close any dialogs that might appear
        try_close_dialogs(driver)
        
        # Log available buttons
        buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        logger.info(f"Found {len(buttons)} buttons on the page")
        for i, btn in enumerate(buttons[:10]):  # Show first 10 buttons
            text = btn.text.strip() if btn.text.strip() else "[No text]"
            logger.info(f"  Button {i+1}: {text} - Class: {btn.get_attribute('class')}")
        
        # Look for check-in button
        logger.info("Looking for check-in button")
        checkin_buttons = driver.find_elements(By.CSS_SELECTOR, "button.el-button.el-button--primary.css-btn")
        
        if checkin_buttons:
            logger.info(f"Found {len(checkin_buttons)} check-in buttons")
            # Click the first available check-in button
            safe_click(driver, checkin_buttons[0])
            logger.info("Clicked check-in button")
            time.sleep(3)
            
            # Check for success message/notification
            success_elements = driver.find_elements(By.CSS_SELECTOR, ".el-message--success, .el-notification__content")
            if success_elements:
                logger.info("Check-in successful: found success notification")
                return True
            else:
                logger.info("Check-in action completed but no success notification found")
                return True
        else:
            logger.warning("No check-in button found - might already be checked in")
            return False
    except Exception as e:
        logger.error(f"Error performing check-in: {e}")
        return False

# Function to vote for meme project on Coresky
def vote_for_meme_project(driver):
    try:
        # Make sure we're on the tasks-rewards page
        if not driver.current_url.startswith(CORESKY_TASKS_URL):
            logger.info(f"Navigating to tasks-rewards page: {CORESKY_TASKS_URL}")
            driver.get(CORESKY_TASKS_URL)
            time.sleep(5)
        
        # Try to close any dialogs that might appear
        try_close_dialogs(driver)
        
        # Look for vote meme button
        logger.info("Looking for vote meme button")
        vote_buttons = driver.find_elements(By.CSS_SELECTOR, "div.btn-meme")
        
        if vote_buttons:
            logger.info("Found vote meme button, clicking")
            safe_click(driver, vote_buttons[0])
            time.sleep(3)
            
            # Enter project name
            logger.info(f"Entering project name: {MEME_PROJECT_NAME}")
            project_inputs = driver.find_elements(By.CSS_SELECTOR, "input.el-input__inner")
            if project_inputs:
                project_inputs[0].clear()
                project_inputs[0].send_keys(MEME_PROJECT_NAME)
                time.sleep(1)
                
                # Press Enter to search for the project
                logger.info("Pressing Enter to search for project")
                webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
                time.sleep(3)
                
                # Log all images found for debugging
                images = driver.find_elements(By.TAG_NAME, "img")
                logger.info(f"Found {len(images)} images on the page")
                
                # Click the vote icon
                logger.info("Looking for vote icon")
                vote_icons = driver.find_elements(By.CSS_SELECTOR, "img[src*='data:image/png;base64'][src*='iVBORw0KGgoAAAANSUhEUgAAADIAAAAzCAYAAADVY1sU']")
                
                if not vote_icons:
                    # Try a more general selector
                    vote_icons = driver.find_elements(By.CSS_SELECTOR, "img[alt='vote']")
                
                if vote_icons:
                    logger.info("Found vote icon, clicking")
                    safe_click(driver, vote_icons[0])
                    time.sleep(3)
                    
                    # Enter points
                    logger.info(f"Entering vote points: {MEME_VOTE_POINTS}")
                    
                    # Try direct input
                    points_inputs = driver.find_elements(By.CSS_SELECTOR, "input.el-input__inner[type='number'], .el-input-number input")
                    if points_inputs:
                        logger.info("Found points input field")
                        points_inputs[0].clear()
                        points_inputs[0].send_keys(MEME_VOTE_POINTS)
                        time.sleep(1)
                    else:
                        logger.warning("Could not find points input field")
                    
                    # Click the confirm vote button
                    logger.info("Looking for confirm vote button")
                    confirm_buttons = driver.find_elements(By.CSS_SELECTOR, "button.el-button.el-button--primary.el-button--large")
                    
                    if confirm_buttons:
                        logger.info("Found confirm vote button, clicking")
                        safe_click(driver, confirm_buttons[0])
                        time.sleep(3)
                        
                        # Check for success message/notification
                        success_elements = driver.find_elements(By.CSS_SELECTOR, ".el-message--success, .el-notification__content")
                        if success_elements:
                            logger.info("Vote successful: found success notification")
                            return True
                        else:
                            logger.info("Vote action completed but no success notification found")
                            return True
                    else:
                        logger.warning("Could not find confirm vote button")
                else:
                    logger.warning("Could not find vote icon")
            else:
                logger.warning("Could not find project name input field")
        else:
            logger.warning("Could not find vote meme button")
        
        return False
    except Exception as e:
        logger.error(f"Error voting for meme project: {e}")
        return False

# Helper function to try closing dialogs
def try_close_dialogs(driver):
    try:
        # Look for dialog overlay
        dialogs = driver.find_elements(By.CSS_SELECTOR, "div.el-overlay-dialog, div.el-dialog__wrapper, .el-message-box__wrapper")
        if not dialogs:
            return False
            
        logger.info(f"Found {len(dialogs)} dialogs that may block interaction")
        
        # Try to find and click close buttons in any dialog
        close_buttons = driver.find_elements(By.CSS_SELECTOR, ".el-dialog__close, .el-message-box__headerbtn, .el-notification__closeBtn, button.el-button")
        if close_buttons:
            for btn in close_buttons:
                try:
                    logger.info("Found close button, clicking it with JavaScript...")
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.5)
                except:
                    pass
        
        # Try pressing ESC key
        try:
            logger.info("Pressing ESC key to close dialog...")
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(0.5)
        except:
            pass
            
        return True
    except Exception as e:
        logger.error(f"Error in dialog handling: {e}")
        return False

# Test function for Coresky functionality
def test_coresky_functions():
    driver = None
    try:
        # Initialize Chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        
        logger.info("Starting Chrome browser")
        driver = webdriver.Chrome(options=options)
        
        # Test options:
        print("\nSelect a test to run:")
        print("1. Test check-in functionality")
        print("2. Test vote for meme functionality")
        print("3. Test both check-in and vote")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            logger.info("Testing check-in functionality")
            perform_coresky_checkin(driver)
        elif choice == "2":
            logger.info("Testing vote for meme functionality")
            vote_for_meme_project(driver)
        elif choice == "3":
            logger.info("Testing both check-in and vote functionality")
            perform_coresky_checkin(driver)
            vote_for_meme_project(driver)
        else:
            logger.error("Invalid choice. Please enter 1, 2, or 3.")
                
        # Keep browser open for manual inspection
        logger.info("Test completed. Browser will remain open for inspection.")
        logger.info("You can manually interact with the page to see what elements are available")
        while True:
            time.sleep(10)
            
    except Exception as e:
        logger.error(f"Error during test: {e}")
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")

if __name__ == "__main__":
    test_coresky_functions() 