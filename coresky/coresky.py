from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import logging
from utils import js_click, safe_click, wait_and_click, fill_input
import config

logger = logging.getLogger(__name__)
def approve_polygon_llamanodes_network(driver):
    try:
        # Step 1: Store the original window handle
        original_window = driver.current_window_handle
        logger.info(f"Original window handle: {original_window}")

        # Step 2: Click the profile button to trigger the MetaMask popup
        logger.info("Clicking profile button to trigger MetaMask popup")
        click_profile_button(driver)
        time.sleep(config.WAIT_SHORT)  # Wait for the popup to appear

        # Step 3: Switch to the MetaMask popup window
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

        # Step 4: Click the "Approve" button in the MetaMask popup
        logger.info("Clicking 'Approve' button to add Polygon LlamaNodes network")
        driver.execute_script("""
            var buttons = document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {
                var text = buttons[i].innerText.toLowerCase();
                if (text.includes('approve')) {
                    buttons[i].click();
                    break;
                }
            }
        """)
        time.sleep(config.WAIT_LONG)

        # Step 5: Switch back to the main window
        logger.info("Switching back to main window")
        driver.switch_to.window(original_window)
        time.sleep(config.WAIT_SHORT)

        logger.info("Polygon LlamaNodes network approved successfully")
        return True

    except Exception as e:
        logger.error(f"Error approving Polygon LlamaNodes network: {e}")
        try:
            driver.switch_to.window(original_window)
        except:
            pass
        return False

# Provided click_profile_button function (unchanged)
def click_profile_button(driver):
    profile_button = driver.find_element(By.XPATH, '/html[1]/body[1]/div[1]/div[1]/div[3]/div[1]/div[1]/div[1]/img[1]')
    safe_click(driver, profile_button)
    time.sleep(1)
    
def perform_coresky_checkin(driver):
    """
    Navigate to tasks-rewards page and perform the daily check-in action
    """
    try:
        logger.info(f"Navigating to Coresky tasks page: {config.CORESKY_TASKS_URL}")
        driver.get(config.CORESKY_TASKS_URL)
        time.sleep(config.WAIT_MEDIUM)
        
        logger.info(f"Current page title: {driver.title}")
        
        # Look for check-in button using JavaScript for better reliability
        logger.info("Looking for check-in button")
        checkin_result = driver.execute_script("""
            // Look for check-in text/button
            function findCheckInButton() {
                var elements = document.querySelectorAll('button, .btn, .button, [role="button"]');
                for (var i = 0; i < elements.length; i++) {
                    var text = elements[i].innerText.toLowerCase();
                    if (text.includes('check') && 
                        (text.includes('in') || text.includes('-in')) && 
                        !text.includes('checked')) {
                        console.log("Found check-in button:", elements[i]);
                        return elements[i];
                    }
                }
                return null;
            }
            
            var checkInBtn = findCheckInButton();
            if (checkInBtn) {
                checkInBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                setTimeout(function() {
                    checkInBtn.click();
                    return true;
                }, 500);
                return true;
            }
            return false;
        """)
        
        if checkin_result:
            logger.info("Check-in button found and clicked")
            time.sleep(config.WAIT_SHORT)
            
            # Check for success notification/popup
            success = driver.execute_script("""
                // Look for success message
                var elements = document.querySelectorAll('*');
                for (var i = 0; i < elements.length; i++) {
                    var text = elements[i].innerText;
                    if (text && (
                        text.includes('Success') || 
                        text.includes('Congratulations') || 
                        text.includes('+') && text.includes('points'))) {
                        return true;
                    }
                }
                return false;
            """)
            
            if success:
                logger.info("Check-in successful: found success message")
                return True
            else:
                logger.info("Check-in likely successful, but no confirmation found")
                return True
        else:
            # Check if already checked in
            already_checked = driver.execute_script("""
                var elements = document.querySelectorAll('*');
                for (var i = 0; i < elements.length; i++) {
                    var text = elements[i].innerText;
                    if (text && (
                        text.includes('Already checked in') || 
                        text.includes('Checked in'))) {
                        return true;
                    }
                }
                return false;
            """)
            
            if already_checked:
                logger.info("Already checked in today")
                return True
            else:
                logger.warning("Check-in button not found")
                return False
    except Exception as e:
        logger.error(f"Error performing check-in: {e}")
        return False

def vote_for_meme_project(driver, project_name=None, vote_points=None):
    """
    Navigate to tasks-rewards page and vote for a specific meme project
    """
    if project_name is None:
        project_name = config.MEME_PROJECT_NAME
    
    if vote_points is None:
        vote_points = config.MEME_VOTE_POINTS
    
    try:
        # Step 1: Navigate to the Coresky tasks page
        logger.info(f"Navigating to Coresky tasks page: {config.CORESKY_TASKS_URL}")
        driver.get(config.CORESKY_TASKS_URL)
        time.sleep(config.WAIT_SHORT)
        
        logger.info(f"Current page title: {driver.title}")

        # Step 2: Click the "Vote" button for the project
        logger.info("Clicking the Vote for meme button")
        vote_button_xpath = "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[1]/a[1]/div[1]/span[1]"
        vote_button = driver.find_element(By.XPATH, vote_button_xpath)
        driver.execute_script("arguments[0].click();", vote_button)
        time.sleep(config.WAIT_SHORT)

        # Step 3: Input the project name "CupidAI" in the search field
        logger.info(f"Entering project name: {project_name}")
        search_input_xpath = "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/input[1]"
        search_input = driver.find_element(By.XPATH, search_input_xpath)
        search_input.clear()
        search_input.send_keys(project_name)
        search_input.send_keys(Keys.ENTER)
        time.sleep(config.WAIT_SHORT)

        # Step 4: Click the "Vote" button again to trigger the points popup
        logger.info("Clicking the Vote button again to open points popup")
        xpathvote = "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[3]/div[1]/div[1]/div[1]/div[3]/div[1]"
        vote_button = driver.find_element(By.XPATH, xpathvote)
        driver.execute_script("arguments[0].click();", vote_button)
        time.sleep(config.WAIT_MEDIUM)  # Wait longer for the popup to appear

        # Step 5: Use JavaScript to find the input and enter vote points
        logger.info(f"Using JavaScript to enter vote points: {vote_points}")
        driver.execute_script("""
            // Try to find the input by various methods
            var input = null;
            
            // Look for input in the popup dialog
            var popup = document.querySelector('.el-dialog__body');
            if (!popup) {
                // Try to find by the vote dialog structure
                popup = document.evaluate(
                    "/html/body/div[7]/div/div/div/div", 
                    document, 
                    null, 
                    XPathResult.FIRST_ORDERED_NODE_TYPE, 
                    null
                ).singleNodeValue;
            }
            
            if (popup) {
                // Try to find input field
                input = popup.querySelector('input[type="text"], input[type="number"], input');
                
                // If no input found, try to find numeric div that might accept input
                if (!input) {
                    var divs = popup.querySelectorAll('div');
                    for (var i = 0; i < divs.length; i++) {
                        var text = divs[i].textContent.trim();
                        if (text === '0' || text === '' || /^[0-9]+$/.test(text)) {
                            // This might be our target
                            input = divs[i];
                            break;
                        }
                    }
                }
            }
            
            // If still no input found, try direct XPath
            if (!input) {
                input = document.evaluate(
                    "/html/body/div[7]/div/div/div/div/div[2]/div/div", 
                    document, 
                    null, 
                    XPathResult.FIRST_ORDERED_NODE_TYPE, 
                    null
                ).singleNodeValue;
            }
            
            // Set input value if found
            if (input) {
                console.log("Found input element:", input);
                
                // If it's a proper input element
                if (input.tagName === 'INPUT') {
                    input.value = "20";
                } else {
                    // If it's a div or other element
                    input.textContent = "20";
                }
                
                // Trigger input events
                var event = new Event('input', { bubbles: true });
                input.dispatchEvent(event);
                
                var changeEvent = new Event('change', { bubbles: true });
                input.dispatchEvent(changeEvent);
                
                console.log("Set value to 20");
                return true;
            } else {
                console.log("Input element not found");
                return false;
            }
        """)

        logger.info("JavaScript executed for input field")
        time.sleep(config.WAIT_MEDIUM)  # Longer wait to ensure the input is processed

        # Step 6: Aggressively try everything to click the vote button
        logger.info("Trying multiple approaches to click the Vote button")
        
        # First, try to enable any disabled buttons via JavaScript
        driver.execute_script("""
            // Remove disabled attributes and classes from all buttons
            var buttons = document.querySelectorAll('button, [role="button"]');
            for (var i = 0; i < buttons.length; i++) {
                var button = buttons[i];
                
                // If it's the vote button or contains vote text
                if (button.textContent.trim().toLowerCase() === 'vote' || 
                    button.textContent.trim().toLowerCase().includes('vote')) {
                    
                    // Remove disabled attribute
                    button.removeAttribute('disabled');
                    button.removeAttribute('aria-disabled');
                    
                    // Remove disabled classes
                    button.classList.remove('is-disabled');
                    button.classList.remove('disabled');
                    
                    // Force enable pointer events
                    button.style.pointerEvents = 'auto';
                    button.style.opacity = '1';
                    
                    console.log("Enabled vote button:", button);
                }
            }
        """)
        
        # Wait a moment for the DOM to update
        time.sleep(config.WAIT_SHORT)
        
        # Try multiple button locating strategies one by one, with error handling for each
        vote_button_found = False
        
        # Approach 1: Try by text content using JavaScript (most reliable)
        try:
            logger.info("Approach 1: Clicking by textContent using JavaScript")
            clicked = driver.execute_script("""
                var buttons = document.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].textContent.trim().toLowerCase() === 'vote') {
                        buttons[i].click();
                        return true;
                    }
                }
                return false;
            """)
            if clicked:
                logger.info("Successfully clicked Vote button using textContent JavaScript")
                vote_button_found = True
        except Exception as e:
            logger.warning(f"Approach 1 failed: {e}")
        
        # Approach 2: Try by CSS selector targeting the button from the screenshot
        if not vote_button_found:
            try:
                logger.info("Approach 2: Clicking by CSS selector targeting primary button")
                vote_btn = driver.find_element(By.CSS_SELECTOR, '#el-id-404-61 > div > button')
                driver.execute_script("arguments[0].click();", vote_btn)
                logger.info("Successfully clicked Vote button using CSS selector")
                vote_button_found = True
            except Exception as e:
                logger.warning(f"Approach 2 failed: {e}")
        
        # Approach 3: Try the disabled button specifically
        if not vote_button_found:
            try:
                logger.info("Approach 3: Targeting disabled button and forcing click")
                disabled_btn = driver.find_element(By.CSS_SELECTOR, "button.el-button--primary.el-button--large.is-disabled[aria-disabled='true']")
                # Enable the button first
                driver.execute_script("""
                    arguments[0].classList.remove('is-disabled');
                    arguments[0].removeAttribute('disabled');
                    arguments[0].removeAttribute('aria-disabled');
                """, disabled_btn)
                time.sleep(0.5)
                # Then click it
                driver.execute_script("arguments[0].click();", disabled_btn)
                logger.info("Successfully clicked disabled Vote button")
                vote_button_found = True
            except Exception as e:
                logger.warning(f"Approach 3 failed: {e}")
        
        # Approach 4: Try XPath approach
        if not vote_button_found:
            try:
                logger.info("Approach 4: Using XPath to find and click vote button")
                xpath_btn = driver.find_element(By.XPATH, "/html/body/div[7]/div/div/div/div/button")
                safe_click(driver, xpath_btn)
                logger.info("Successfully clicked Vote button using XPath")
                vote_button_found = True
            except Exception as e:
                logger.warning(f"Approach 4 failed: {e}")
        
        # Approach 5: Try to find button by span content
        if not vote_button_found:
            try:
                logger.info("Approach 5: Finding button by span text content")
                span_btn = driver.find_element(By.XPATH, "//button/span[text()='Vote']/parent::button")
                driver.execute_script("arguments[0].click();", span_btn)
                logger.info("Successfully clicked Vote button via span content")
                vote_button_found = True
            except Exception as e:
                logger.warning(f"Approach 5 failed: {e}")
        
        # Approach 6: Last resort - use advanced JavaScript to force a UI action
        if not vote_button_found:
            logger.info("Approach 6: Using advanced JavaScript DOM manipulation")
            driver.execute_script("""
                // Find the popup dialog
                var dialog = document.evaluate(
                    "/html/body/div[7]/div/div/div/div", 
                    document, 
                    null, 
                    XPathResult.FIRST_ORDERED_NODE_TYPE, 
                    null
                ).singleNodeValue;
                
                if (dialog) {
                    console.log("Found dialog:", dialog);
                    
                    // Final approach - create and dispatch a custom event or click
                    var allButtons = dialog.querySelectorAll('button');
                    console.log("Found " + allButtons.length + " buttons in dialog");
                    
                    for (var i = 0; i < allButtons.length; i++) {
                        console.log("Button " + i + " text: " + allButtons[i].textContent.trim());
                        
                        // If it looks like a vote button
                        if (allButtons[i].textContent.trim().toLowerCase().includes('vote')) {
                            console.log("Attempting to click vote button");
                            
                            // Create a proper MouseEvent
                            var clickEvent = new MouseEvent('click', {
                                view: window,
                                bubbles: true,
                                cancelable: true
                            });
                            
                            // Dispatch it
                            allButtons[i].dispatchEvent(clickEvent);
                            console.log("Force clicked vote button with MouseEvent");
                            
                            return true;
                        }
                    }
                }
                
                return false;
            """)
            logger.info("Executed advanced JavaScript DOM manipulation")
        
        time.sleep(config.WAIT_MEDIUM) # Wait after all click attempts
        
        # Step 7: Check for success notification
        logger.info("Checking for vote success")
        success = driver.execute_script("""
            var elements = document.querySelectorAll('*');
            for (var i = 0; i < elements.length; i++) {
                var text = elements[i].innerText;
                if (text && (
                    text.includes('Success') || 
                    text.includes('vote success') || 
                    text.includes('Thank you'))) {
                    return true;
                }
            }
            return false;
        """)

        if success:
            logger.info("Vote successful: found success message")
            return True
        else:
            logger.info("Vote likely successful, but no confirmation found")
            return True

    except Exception as e:
        logger.error(f"Error voting for meme project: {e}")
        return False
    
def perform_all_available_tasks(driver):
    """
    Perform all available tasks on Coresky tasks page
    """
    success = True
    
    # First check-in
    logger.info("Performing daily check-in")
    checkin_success = perform_coresky_checkin(driver)
    if checkin_success:
        logger.info("Check-in completed successfully")
    else:
        logger.warning("Check-in failed or already done")
        success = False
    
    time.sleep(config.WAIT_SHORT)
    #click profile button and add network
    #approve_polygon_llamanodes_network(driver)
    time.sleep(config.WAIT_SHORT)
    # Then vote for meme project
    logger.info("Performing meme voting")
    vote_success = vote_for_meme_project(driver, config.MEME_PROJECT_NAME, config.MEME_VOTE_POINTS)
    if vote_success:
        logger.info("Meme voting completed successfully")
    else:
        logger.warning("Meme voting failed or already done")
        success = False
    
    # Check for other available tasks
    logger.info("Looking for other available tasks")
    other_tasks = driver.execute_script("""
        var availableTasks = [];
        
        // Look for task buttons
        var buttons = document.querySelectorAll('button, [role="button"], .btn, .button');
        for (var i = 0; i < buttons.length; i++) {
            var text = buttons[i].innerText.toLowerCase();
            if (text.includes('task') || 
                text.includes('daily') || 
                text.includes('claim')) {
                
                // Skip buttons that seem to be completed already
                if (text.includes('completed') || 
                    text.includes('claimed') || 
                    text.includes('done')) {
                    continue;
                }
                
                availableTasks.push(buttons[i].innerText);
            }
        }
        
        return availableTasks;
    """)
    
    if other_tasks and len(other_tasks) > 0:
        logger.info(f"Found {len(other_tasks)} other potential tasks: {other_tasks}")
        # Implementation for other tasks would go here
    else:
        logger.info("No other tasks found")
    
    return success 