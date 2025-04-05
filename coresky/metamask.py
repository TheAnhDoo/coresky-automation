from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import logging
from utils import js_click, safe_click, wait_and_click, fill_input
import config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
logger = logging.getLogger(__name__)

# Configuration
METAMASK_EXTENSION_ID = "nkbihfbeogaeaoehlefnkodbefgpgknn"
METAMASK_PASSWORD = "123123123"

# Function to set up a new MetaMask wallet
def setup_metamask_wallet(driver, take_screenshots=True):
    try:
        # Store the original window handle to ensure we stay in the same tab
        original_window = driver.current_window_handle
        logger.info(f"Original window handle: {original_window}")

        # Navigate directly to MetaMask extension page
        logger.info("Opening MetaMask extension")
        driver.get(f"chrome-extension://{config.METAMASK_EXTENSION_ID}/home.html")
        time.sleep(config.WAIT_SHORT)

        # Check for new tabs and close them, ensuring we stay in the original tab
        if len(driver.window_handles) > 1:
            logger.info("New tab detected, closing extra tabs and switching back to original")
            for handle in driver.window_handles:
                if handle != original_window:
                    driver.switch_to.window(handle)
                    driver.close()
            driver.switch_to.window(original_window)
        else:
            logger.info("No new tabs detected, continuing in the original tab")

        # Log current page information
        logger.info(f"Current URL: {driver.current_url}")
        logger.info(f"Current title: {driver.title}")

        # Verify we're on the MetaMask page
        if "MetaMask" not in driver.title:
            logger.warning("Could not access MetaMask extension")
            return False
        
        logger.info("Successfully accessed MetaMask extension")

        # Start the setup procedure
        time.sleep(1)
        logger.info("Looking for terms checkbox")
        accept_terms(driver)
        # time.sleep(config.WAIT_SHORT)
        
        create_wallet_button = find_create_wallet_button(driver)
        if create_wallet_button:
            logger.info("Found create wallet button, clicking")
            success = click_with_js(driver, create_wallet_button)
            if not success:
                logger.error("Failed to click create wallet button")
                return False
            # time.sleep(1)
            
            # Accept terms
            logger.info("Looking for terms checkbox")
            accept_terms(driver)
            
            # Handle I agree to analytics
            logger.info("Looking for analytics agreement")
            agree_to_analytics(driver)
            # time.sleep(1)
            
            # Set password
            logger.info("Setting up password")
            if not setup_password(driver, config.METAMASK_PASSWORD):
                logger.error("Failed to set up password")
                return False
            # time.sleep(0.2)
            
            # Skip Secure Wallet
            logger.info("Attempting to skip secure wallet")
            if not skip_secure_wallet(driver):
                logger.warning("Could not skip secure wallet, but continuing")
            
            # Click done button if found
            logger.info("Looking for done button")
            button1 = driver.find_element(By.XPATH, '//button[normalize-space()="Done"]')
            safe_click(driver, button1)
            # time.sleep(0.25)
            button2 = driver.find_element(By.XPATH, '//button[normalize-space()="Next"]')
            safe_click(driver,button2)
            # time.sleep(0.25)
            button3 = driver.find_element(By.XPATH, '//button[normalize-space()="Done"]')
            safe_click(driver,button3)


            
            logger.info("MetaMask wallet setup completed successfully")
            return True
        else:
            logger.error("Could not find create wallet button")
            return False
            
    except Exception as e:
        logger.error(f"Error setting up MetaMask wallet: {e}")
        return False

def find_create_wallet_button(driver):
    try:
        # First try with standard Selenium
        create_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-testid='onboarding-create-wallet'], button.create-wallet-button")
        if create_buttons and len(create_buttons) > 0:
            return create_buttons[0]
            
        # Try to find by text content
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if button.is_displayed():
                text = button.text.strip().lower()
                if "create" in text and "wallet" in text:
                    return button
                    
        return None
    except Exception as e:
        logger.error(f"Error finding create wallet button: {e}")
        return None

def click_with_js(driver, element):
    try:
        # First try direct click
        try:
            element.click()
            return True
        except:
            # Fall back to JavaScript click
            driver.execute_script("arguments[0].click();", element)
            return True
    except Exception as e:
        logger.error(f"Error clicking element: {e}")
        
        # Last resort: use direct JavaScript search and click
        button_text = ""
        try:
            button_text = element.text.lower()
        except:
            pass
            
        if "create" in button_text and "wallet" in button_text:
            try:
                driver.execute_script("""
                    var buttons = document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        var text = buttons[i].innerText.toLowerCase();
                        if (text.includes('create') && text.includes('wallet')) {
                            buttons[i].click();
                            return true;
                        }
                    }
                """)
                return True
            except:
                pass
                
        return False

def accept_terms(driver):
    try:
        # Try standard Selenium first
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input#onboarding__terms-checkbox, input[type='checkbox']")
        if checkboxes and len(checkboxes) > 0:
            for checkbox in checkboxes:
                if checkbox.is_displayed():
                    safe_click(driver, checkbox)
                    return True
                    
        # Try with JavaScript
        driver.execute_script("""
            var checkboxes = document.querySelectorAll('input[type="checkbox"]');
            for (var i = 0; i < checkboxes.length; i++) {
                if (window.getComputedStyle(checkboxes[i]).display !== 'none') {
                    checkboxes[i].checked = true;
                    checkboxes[i].dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                }
            }
        """)
        return True
    except Exception as e:
        logger.error(f"Error accepting terms: {e}")
        return False
        
def agree_to_analytics(driver):
    try:
        # Try standard Selenium
        agree_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-testid='metametrics-i-agree'], button.btn-primary")
        if agree_buttons and len(agree_buttons) > 0:
            for button in agree_buttons:
                if button.is_displayed():
                    safe_click(driver, button)
                    return True
                    
        # Try by text content
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if button.is_displayed() and "agree" in button.text.lower():
                safe_click(driver, button)
                return True
                
        # Try with JavaScript
        driver.execute_script("""
            var buttons = document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {
                var text = buttons[i].innerText.toLowerCase();
                if (text.includes('agree')) {
                    buttons[i].click();
                    return true;
                }
            }
        """)
        return True
    except Exception as e:
        logger.error(f"Error agreeing to analytics: {e}")
        return False
        
def setup_password(driver, password):
    try:
        # Try standard Selenium
        password_fields = driver.find_elements(By.CSS_SELECTOR, "input[data-testid='create-password-new'], input[data-testid='create-password-confirm'], input[type='password']")
        if password_fields and len(password_fields) >= 2:
            for field in password_fields:
                if field.is_displayed():
                    field.clear()
                    field.send_keys(password)
            
            # Check terms checkbox if present
            checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[data-testid='create-password-terms'], input[type='checkbox']")
            for checkbox in checkboxes:
                if checkbox.is_displayed() and not checkbox.is_selected():
                    safe_click(driver, checkbox)
            
            # Click create button
            create_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-testid='create-password-wallet'], button.btn-primary")
            for button in create_buttons:
                if button.is_displayed():
                    safe_click(driver, button)
                    return True
                    
        # Try with JavaScript
        success = driver.execute_script(f"""
            var password = "{password}";
            var passwordFields = document.querySelectorAll('input[type="password"]');
            for (var i = 0; i < passwordFields.length; i++) {{
                passwordFields[i].value = password;
                passwordFields[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            
            var checkboxes = document.querySelectorAll('input[type="checkbox"]');
            for (var i = 0; i < checkboxes.length; i++) {{
                checkboxes[i].checked = true;
                checkboxes[i].dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            
            var buttons = document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {{
                var text = buttons[i].innerText.toLowerCase();
                if (text.includes('create')) {{
                    buttons[i].click();
                    return true;
                }}
            }}
            return false;
        """)
        
        return success if isinstance(success, bool) else True
    except Exception as e:
        logger.error(f"Error setting up password: {e}")
        return False
        
def skip_secure_wallet(driver):
    try:
        # # Try skip buttons with various selectors
        
        # skip_selectors = [
        #     "button[data-testid='skip-srp-backup']", 
        #     "button.btn-secondary", 
        #     "button.mm-button-secondary"
        # ]
        
        # for selector in skip_selectors:
        #     buttons = driver.find_elements(By.CSS_SELECTOR, selector)
        #     for button in buttons:
        #         if button.is_displayed() and ("skip" in button.text.lower() or "remind" in button.text.lower()):
        #             safe_click(driver, button)
        #             time.sleep(config.WAIT_SHORT)
                    
        #             # Handle confirmation checkbox if presented
        #             checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        #             for checkbox in checkboxes:
        #                 if checkbox.is_displayed():
        #                     safe_click(driver, checkbox)
        #                     time.sleep(1)
                    
        #             # Click final skip/confirm button
        #             confirm_buttons = driver.find_elements(By.CSS_SELECTOR, "button.btn-primary")
        #             for confirm in confirm_buttons:
        #                 if confirm.is_displayed():
        #                     safe_click(driver, confirm)
        #                     return True
                            
        # # Try with JavaScript
        # success = driver.execute_script("""
        #     function findButtonWithText(text) {
        #         var buttons = document.querySelectorAll('button');
        #         for (var i = 0; i < buttons.length; i++) {
        #             if (buttons[i].innerText.toLowerCase().includes(text)) {
        #                 return buttons[i];
        #             }
        #         }
        #         return null;
        #     }
            
        #     var skipButton = findButtonWithText('skip') || findButtonWithText('remind');
        #     if (skipButton) {
        #         skipButton.click();
        #         setTimeout(function() {
        #             var checkboxes = document.querySelectorAll('input[type="checkbox"]');
        #             for (var i = 0; i < checkboxes.length; i++) {
        #                 checkboxes[i].checked = true;
        #                 checkboxes[i].dispatchEvent(new Event('change', { bubbles: true }));
        #             }
                    
        #             setTimeout(function() {
        #                 var confirmButton = findButtonWithText('skip') || findButtonWithText('confirm');
        #                 if (confirmButton) {
        #                     confirmButton.click();
        #                     return true;
        #                 }
        #             }, 500);
        #         }, 500);
        #         return true;
        #     }
        #     return false;
        # """) /html/body/div[1]/div/div[2]/div/div/div/div[3]/button[1]
        #return success if isinstance(success, bool) else True        
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/div[3]/button[1]").click()
        driver.find_element(By.XPATH, "/html/body/div[2]/div/div/section/div[1]/div/div/label/input").click()
        driver.find_element(By.XPATH, "/html/body/div[2]/div/div/section/div[2]/div/button[2]").click()
        return True

    except Exception as e:
        logger.error(f"Error skipping secure wallet: {e}")
        return False
        
def click_done_button(driver):
    try:
        # Try standard Selenium
        done_selectors = [
            "button[data-testid='onboarding-complete-done']", 
            "button.btn-primary", 
            "button.mm-box--color-primary-inverse"
            
        ]
        
        for selector in done_selectors:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for button in buttons:
                if button.is_displayed() and ("done" in button.text.lower() or "got it" in button.text.lower()):
                    safe_click(driver, button)
                    return True
                    
        # Try with JavaScript
        success = driver.execute_script("""
            var buttons = document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {
                var text = buttons[i].innerText.toLowerCase();
                if (text.includes('done') || text.includes('got it')) {
                    buttons[i].click();
                    return true;
                }
            }
            return false;
        """)
        
        return success if isinstance(success, bool) else True
    except Exception as e:
        logger.error(f"Error clicking done button: {e}")
        return False

# Function to connect MetaMask to Coresky
def connect_metamask_to_coresky(driver, coresky_url):
    try:
        # Navigate to Coresky
        logger.info(f"Navigating to Coresky: {coresky_url}")
        driver.get(coresky_url)
        time.sleep(config.WAIT_MEDIUM)

        # Click the "Connect Wallet" button
        logger.info("Looking for Connect Wallet button")
        try:
            connect_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.head-connect:nth-child(1) > span:nth-child(2)"))
            )
            logger.info("Connect Wallet button found, clicking it")
            safe_click(driver, connect_button)
            time.sleep(config.WAIT_SHORT)
        except Exception as e:
            logger.warning(f"Connect Wallet button not found or not clickable: {e}")
            return False

        # Click the MetaMask option
        logger.info("Looking for MetaMask option")
        try:
            # Use a more robust selector for the MetaMask option
            metamask_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.item:nth-child(1) > img:nth-child(1)"))
            )
            logger.info("MetaMask option found, clicking it")
            safe_click(driver, metamask_option)
            time.sleep(config.WAIT_SHORT)
        except Exception as e:
            logger.warning(f"MetaMask option not found or not clickable: {e}")
            return False

        # Store the original window handle
        original_window = driver.current_window_handle
        logger.info(f"Original window handle: {original_window}")

        # Switch to the MetaMask popup window
        logger.info("Looking for MetaMask popup window")
        metamask_popup = None
        for handle in driver.window_handles:
            if handle != original_window:
                driver.switch_to.window(handle)
                if "MetaMask" in driver.title:
                    metamask_popup = handle
                    logger.info(f"Found MetaMask popup: {driver.title}")
                    break

        if not metamask_popup:
            logger.warning("MetaMask popup not found")
            driver.switch_to.window(original_window)
            return False

        # Approve the connection in the MetaMask popup
        logger.info("Approving MetaMask connection")
        driver.execute_script("""
            var buttons = document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {
                var text = buttons[i].innerText.toLowerCase();
                if (text.includes('next') || text.includes('connect')) {
                    buttons[i].click();
                    break;
                }
            }
        """)
        time.sleep(config.WAIT_SHORT)

        # Click the final connect/confirm button
        logger.info("Clicking final connect/confirm button in MetaMask popup")
        driver.execute_script("""
            var buttons = document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {
                var text = buttons[i].innerText.toLowerCase();
                if (text.includes('connect') || text.includes('confirm')) {
                    buttons[i].click();
                    break;
                }
            }
        """)
        time.sleep(config.WAIT_MEDIUM)

        # Handle the signing request (if a new popup appears for signing)
        logger.info("Looking for MetaMask signing popup")
        for handle in driver.window_handles:
            if handle != original_window and handle != metamask_popup:
                driver.switch_to.window(handle)
                if "MetaMask" in driver.title:
                    logger.info(f"Found MetaMask signing popup: {driver.title}")
                    driver.execute_script("""
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = buttons[i].innerText.toLowerCase();
                            if (text.includes('Confirm') || text.includes('confirm')) {
                                buttons[i].click();
                                break;
                            }
                        }
                    """)
                    time.sleep(config.WAIT_SHORT)
                    time.sleep(5)
                    break

        # Switch back to the main Coresky window
        logger.info("Switching back to main Coresky window")
        driver.switch_to.window(original_window)
        time.sleep(config.WAIT_SHORT)

        logger.info("MetaMask connection and signing completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error connecting MetaMask to Coresky: {e}")
        try:
            driver.switch_to.window(original_window)
        except:
            pass
        return False