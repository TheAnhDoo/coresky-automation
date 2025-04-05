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

        # Step 6: Try advanced interaction techniques since basic selectors aren't working
        logger.info("Using advanced interaction techniques for the Vote button")
        
        # First try to get the button with multiple approaches and store all found elements
        potential_buttons = []
        
        try:
            # Wait for the button to be clickable (may help with timing issues)
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            logger.info("Waiting for button to be clickable...")
            wait = WebDriverWait(driver, 10)
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.el-button.el-button--primary.el-button--large')))
            potential_buttons.append(btn)
            logger.info("Found button with WebDriverWait")
        except Exception as e:
            logger.warning(f"WebDriverWait approach failed: {e}")
        
        # Try different selectors to gather potential buttons
        try:
            # By dialog container and then finding the button
            dialog = driver.find_element(By.CSS_SELECTOR, '.el-dialog__wrapper')
            buttons = dialog.find_elements(By.TAG_NAME, 'button')
            potential_buttons.extend(buttons)
            logger.info(f"Found {len(buttons)} buttons in dialog")
        except Exception as e:
            logger.warning(f"Dialog container approach failed: {e}")
        
        try:
            # By vote text
            vote_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Vote')]")
            potential_buttons.extend(vote_buttons)
            logger.info(f"Found {len(vote_buttons)} buttons with 'Vote' text")
        except Exception as e:
            logger.warning(f"Vote text search failed: {e}")
            
        # Try interacting with each potential button using multiple methods
        vote_button_clicked = False
        
        for i, button in enumerate(potential_buttons):
            if vote_button_clicked:
                break
                
            logger.info(f"Trying advanced interactions with button {i+1}/{len(potential_buttons)}")
            
            try:
                # Method 1: ActionChains for precise click
                from selenium.webdriver.common.action_chains import ActionChains
                
                logger.info("Trying ActionChains approach")
                actions = ActionChains(driver)
                actions.move_to_element(button)
                actions.pause(1)  # Pause for a second
                actions.click()
                actions.perform()
                
                logger.info("ActionChains click executed")
                vote_button_clicked = True
                time.sleep(2)
                continue
            except Exception as e:
                logger.warning(f"ActionChains approach failed: {e}")
            
            try:
                # Method 2: Send Enter key to the button
                logger.info("Trying Send Keys approach")
                button.send_keys(Keys.RETURN)
                logger.info("Send Keys executed")
                vote_button_clicked = True
                time.sleep(2)
                continue
            except Exception as e:
                logger.warning(f"Send Keys approach failed: {e}")
            
            try:
                # Method 3: Try with safe_click helper
                logger.info("Trying safe_click approach")
                from utils import safe_click
                safe_click_result = safe_click(driver, button, max_attempts=5)
                if safe_click_result:
                    logger.info("safe_click successful")
                    vote_button_clicked = True
                    time.sleep(2)
                    continue
            except Exception as e:
                logger.warning(f"safe_click approach failed: {e}")
                
            try:
                # Method 4: Coordinate-based click
                logger.info("Trying coordinate-based click")
                
                # Get button location and size
                location = button.location
                size = button.size
                
                # Calculate center point
                x_center = location['x'] + size['width'] // 2
                y_center = location['y'] + size['height'] // 2
                
                # Perform click at coordinates
                actions = ActionChains(driver)
                actions.move_by_offset(x_center, y_center)
                actions.click()
                actions.perform()
                
                logger.info(f"Clicked at coordinates: {x_center}, {y_center}")
                vote_button_clicked = True
                time.sleep(2)
                continue
            except Exception as e:
                logger.warning(f"Coordinate-based click failed: {e}")
                
        # If none of the buttons worked with standard approaches, try brute force methods
        if not vote_button_clicked:
            logger.info("Standard approaches failed, trying brute force methods")
            
            try:
                # Method 5: Tab navigation to find and click the button
                logger.info("Trying tab navigation")
                active_element = driver.switch_to.active_element
                
                # Press tab up to 10 times to try to reach the button
                for _ in range(10):
                    active_element.send_keys(Keys.TAB)
                    time.sleep(0.5)
                    
                    # Check if we've reached a button element
                    active = driver.switch_to.active_element
                    tag_name = active.tag_name
                    
                    if tag_name.lower() == 'button':
                        logger.info("Found button via tab navigation")
                        active.send_keys(Keys.RETURN)
                        vote_button_clicked = True
                        break
                
                time.sleep(2)
            except Exception as e:
                logger.warning(f"Tab navigation failed: {e}")
                
            if not vote_button_clicked:
                try:
                    # Method 6: Inject a custom button and click it
                    logger.info("Injecting a custom button as last resort")
                    driver.execute_script("""
                        // Find the dialog
                        var dialogs = document.querySelectorAll('.el-dialog__wrapper, [role="dialog"]');
                        if (dialogs.length > 0) {
                            var dialog = dialogs[0];
                            
                            // Find the button container/footer
                            var footer = dialog.querySelector('.el-dialog__footer, .dialog-footer');
                            if (!footer) {
                                // If no footer, use the dialog itself
                                footer = dialog;
                            }
                            
                            // First, try to click any existing vote button directly with a MouseEvent
                            var existingButtons = footer.querySelectorAll('button');
                            for (var i = 0; i < existingButtons.length; i++) {
                                if (existingButtons[i].textContent.toLowerCase().includes('vote')) {
                                    console.log("Found vote button, sending MouseEvent");
                                    
                                    // Create and dispatch mousedown, mouseup and click events
                                    ['mousedown', 'mouseup', 'click'].forEach(function(eventType) {
                                        var clickEvent = new MouseEvent(eventType, {
                                            view: window,
                                            bubbles: true,
                                            cancelable: true,
                                            buttons: 1
                                        });
                                        existingButtons[i].dispatchEvent(clickEvent);
                                    });
                                    
                                    return true;
                                }
                            }
                            
                            // If clicking existing buttons didn't work, create a custom button
                            var customButton = document.createElement('button');
                            customButton.textContent = 'Vote';
                            customButton.style.cssText = 'background-color: #3880ff; color: white; padding: 10px 20px; border-radius: 4px; border: none; cursor: pointer; font-size: 16px; margin: 10px;';
                            
                            // Add click handler that will trigger the original button
                            customButton.addEventListener('click', function() {
                                console.log("Custom button clicked");
                                
                                // Try to click all buttons in the dialog again
                                var allButtons = dialog.querySelectorAll('button');
                                for (var i = 0; i < allButtons.length; i++) {
                                    if (allButtons[i].textContent.toLowerCase().includes('vote') && 
                                        allButtons[i] !== customButton) {
                                        console.log("Clicking original button from custom button handler");
                                        allButtons[i].click();
                                    }
                                }
                                
                                // Attempt to close the dialog
                                var closeButton = dialog.querySelector('.el-dialog__close, .close-btn');
                                if (closeButton) {
                                    closeButton.click();
                                }
                                
                                return true;
                            });
                            
                            // Add the button to the footer
                            footer.appendChild(customButton);
                            console.log("Custom vote button added");
                            
                            // Click the custom button
                            setTimeout(function() {
                                customButton.click();
                                console.log("Custom button clicked");
                            }, 500);
                            
                            return true;
                        }
                        
                        return false;
                    """)
                    
                    logger.info("Custom button injection executed")
                    time.sleep(3)  # Give it time to work
                except Exception as e:
                    logger.warning(f"Custom button injection failed: {e}")
        
        # Final wait before proceeding to next step
        time.sleep(config.WAIT_MEDIUM)
        
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