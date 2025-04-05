from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config

logger = logging.getLogger(__name__)

# Helper function to check for and close dialogs
def close_dialog_if_exists(driver):
    try:
        # Look for dialog overlay
        dialogs = driver.find_elements(By.CSS_SELECTOR, "div.el-overlay-dialog, div.el-dialog__wrapper, .el-message-box__wrapper")
        if not dialogs:
            return False
            
        logger.info(f"Found {len(dialogs)} dialogs that may block interaction")
        
        # Try multiple approaches to close dialogs
        methods_tried = []
        
        # Method 1: Try to find and click close buttons in any dialog
        try:
            close_buttons = driver.find_elements(By.CSS_SELECTOR, ".el-dialog__close, .el-message-box__headerbtn, .el-notification__closeBtn, button.el-button")
            if close_buttons:
                methods_tried.append("close buttons")
                for btn in close_buttons:
                    try:
                        logger.info("Found close button, clicking it with JavaScript...")
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(0.5)
                    except:
                        pass
        except:
            pass
            
        # Method 2: Try to click outside the dialog
        try:
            methods_tried.append("click outside")
            logger.info("Clicking outside dialogs...")
            # Try multiple positions
            positions = [(10, 10), (10, 300), (300, 10)]
            for x, y in positions:
                action = webdriver.ActionChains(driver)
                action.move_by_offset(x, y).click().perform()
                action.reset_actions()
                time.sleep(0.5)
        except:
            pass
            
        # Method 3: Try pressing ESC key
        try:
            methods_tried.append("ESC key")
            logger.info("Pressing ESC key to close dialog...")
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(0.5)
        except:
            pass
            
        # Method 4: Try JavaScript to remove dialogs
        try:
            methods_tried.append("JavaScript removal")
            logger.info("Using JavaScript to forcibly remove dialogs...")
            driver.execute_script("""
                var dialogs = document.querySelectorAll('div.el-overlay-dialog, div.el-dialog__wrapper, .el-message-box__wrapper');
                for(var i=0; i<dialogs.length; i++){
                    dialogs[i].remove();
                }
            """)
            time.sleep(0.5)
        except:
            pass
            
        # Check if dialogs still exist
        try:
            remaining_dialogs = driver.find_elements(By.CSS_SELECTOR, "div.el-overlay-dialog, div.el-dialog__wrapper, .el-message-box__wrapper")
            if remaining_dialogs:
                logger.info(f"Still found {len(remaining_dialogs)} dialogs after trying: {', '.join(methods_tried)}")
                return False
            else:
                logger.info("Successfully closed all dialogs")
                return True
        except:
            logger.error("Error checking for remaining dialogs")
            return False
                
    except Exception as e:
        logger.error(f"Error in dialog handling: {e}")
        return False

# Function to click using pure JavaScript
def js_click(driver, element):
    try:
        logger.info("Using pure JavaScript click")
        # Execute JavaScript to click the element directly
        driver.execute_script("""
            var element = arguments[0];
            
            // Create a synthetic mouse event
            var clickEvent = document.createEvent('MouseEvents');
            clickEvent.initEvent('click', true, true);
            
            // Dispatch the event to the element
            element.dispatchEvent(clickEvent);
        """, element)
        
        logger.info("JavaScript click dispatched")
        return True
    except Exception as e:
        logger.error(f"JavaScript click failed: {e}")
        return False

# Safer click function that handles intercepted clicks
def safe_click(driver, element, max_attempts=3):
    """
    Attempts to click an element safely, handling potential interception.
    Will try multiple methods including:
    1. Direct Selenium click
    2. JavaScript click
    3. Scrolling into view and retrying
    
    Args:
        driver: Selenium WebDriver instance
        element: The element to click
        max_attempts: Maximum number of attempts before giving up
        
    Returns:
        bool: Whether the click was successful
    """
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        try:
            # Try to scroll element into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            
            # Try direct click
            element.click()
            logger.debug(f"Element clicked successfully on attempt {attempts}")
            return True
        except ElementClickInterceptedException:
            logger.debug(f"Click intercepted on attempt {attempts}, trying alternatives")
            
            # Try to identify and close any blocking dialogs
            close_dialog_if_exists(driver)
            
            # Try JavaScript click
            try:
                driver.execute_script("arguments[0].click();", element)
                logger.debug(f"Element clicked with JavaScript on attempt {attempts}")
                return True
            except Exception as js_error:
                logger.debug(f"JavaScript click failed: {js_error}")
                
            if attempts == max_attempts - 1:
                # Last try: use ActionChains
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.move_to_element(element).click().perform()
                    logger.debug("Element clicked with ActionChains")
                    return True
                except Exception as action_error:
                    logger.debug(f"ActionChains click failed: {action_error}")
        except StaleElementReferenceException:
            logger.debug(f"Element became stale on attempt {attempts}")
            return False
        except Exception as e:
            logger.debug(f"Error clicking element on attempt {attempts}: {e}")
            
            # Try JavaScript click as last resort
            try:
                driver.execute_script("arguments[0].click();", element)
                logger.debug(f"Element clicked with JavaScript after error")
                return True
            except:
                pass
                
        time.sleep(1)  # Wait before retrying
    
    logger.warning(f"Failed to click element after {max_attempts} attempts")
    return False

# Function to wait for an element and click it safely
def wait_and_click(driver, selector, by=By.CSS_SELECTOR, timeout=15, description="element"):
    try:
        logger.info(f"Waiting for {description} with selector: {selector}")
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        logger.info(f"Found {description}, attempting to click")
        return safe_click(driver, element)
    except Exception as e:
        logger.error(f"Error waiting for {description}: {e}")
        return False

# Function to fill an input field
def fill_input(driver, selector, text, by=By.CSS_SELECTOR, timeout=15, description="input field"):
    try:
        logger.info(f"Waiting for {description} with selector: {selector}")
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        logger.info(f"Found {description}, clearing existing text")
        element.clear()
        logger.info(f"Entering text: {text}")
        element.send_keys(text)
        return True
    except Exception as e:
        logger.error(f"Error filling {description}: {e}")
        return False 

def take_screenshot(driver, name):
    """
    Takes a screenshot and saves it to the configured screenshots directory
    
    Args:
        driver: Selenium WebDriver instance
        name: Name for the screenshot file (without extension)
        
    Returns:
        str: Path to the saved screenshot or None if failed
    """
    if not config.TAKE_SCREENSHOTS:
        return None
        
    try:
        import os
        
        # Ensure screenshots directory exists
        os.makedirs(config.SCREENSHOTS_DIR, exist_ok=True)
        
        # Add timestamp to avoid overwriting
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(config.SCREENSHOTS_DIR, filename)
        
        driver.save_screenshot(filepath)
        logger.info(f"Screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        return None 