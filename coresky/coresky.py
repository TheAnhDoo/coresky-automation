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
        time.sleep(config.WAIT_SHORT)  # Wait for the popup to appear

        # Step 5: Input points in the popup - focus on the specific xpath you provided
        logger.info(f"Attempting to enter vote points: {vote_points}")
        specific_xpath = "/html/body/div[7]/div/div/div/div/div[2]/div/div"

        try:
            # First try: Direct approach with focused xpath
            logger.info(f"Direct attempt on xpath: {specific_xpath}")
            # Wait a bit longer for the element to be fully available
            time.sleep(3)
            
            # Try multiple approaches for the same element
            
            # Approach 1: Standard Selenium find and send keys
            try:
                input_element = driver.find_element(By.XPATH, specific_xpath)
                driver.execute_script("arguments[0].scrollIntoView(true);", input_element)
                input_element.click()
                input_element.clear()
                input_element.send_keys(vote_points)
                logger.info("Successfully used direct Selenium method")
                
            # Approach 2: Use JavaScript to set value
            except Exception as e1:
                logger.warning(f"First approach failed: {e1}")
                try:
                    logger.info("Trying JavaScript approach")
                    driver.execute_script("""
                        var element = document.evaluate(
                            "/html/body/div[7]/div/div/div/div/div[2]/div/div", 
                            document, 
                            null, 
                            XPathResult.FIRST_ORDERED_NODE_TYPE, 
                            null
                        ).singleNodeValue;
                        
                        if(element) {
                            element.click();
                            element.value = "20";
                            
                            // Create and dispatch events
                            var inputEvent = new Event('input', { bubbles: true });
                            element.dispatchEvent(inputEvent);
                            
                            var changeEvent = new Event('change', { bubbles: true });
                            element.dispatchEvent(changeEvent);
                            
                            console.log("Set value to 20 using JavaScript");
                            return true;
                        }
                        return false;
                    """)
                    logger.info("Successfully used JavaScript method")
                
                # Approach 3: Try fill_input utility
                except Exception as e2:
                    logger.warning(f"Second approach failed: {e2}")
                    try:
                        logger.info("Trying fill_input utility")
                        result = fill_input(driver, specific_xpath, vote_points, By.XPATH, 10, "vote points input")
                        if result:
                            logger.info("Successfully used fill_input utility")
                        else:
                            raise Exception("fill_input returned False")
                    
                    # Approach 4: Manual key simulation with ActionChains
                    except Exception as e3:
                        logger.warning(f"Third approach failed: {e3}")
                        logger.info("Trying ActionChains approach")
                        from selenium.webdriver.common.action_chains import ActionChains
                        
                        # First find the element
                        try:
                            input_element = driver.find_element(By.XPATH, specific_xpath)
                            # Scroll to it
                            driver.execute_script("arguments[0].scrollIntoView(true);", input_element)
                            
                            # Set up action chains
                            actions = ActionChains(driver)
                            actions.move_to_element(input_element)
                            actions.click()
                            actions.send_keys("20")
                            actions.perform()
                            
                            logger.info("Successfully used ActionChains method")
                        except Exception as e4:
                            logger.warning(f"All direct approaches failed: {e4}")
                            # Last attempt: JavaScript direct DOM manipulation
                            logger.info("Using brute force JavaScript approach")
                            driver.execute_script("""
                                // Try to find any input in the vote popup
                                var popup = document.querySelector(".vote-popup, .dialog, .modal, div[role='dialog']");
                                if (!popup) {
                                    // If no popup class, try to get the container at the XPath
                                    popup = document.evaluate(
                                        "/html/body/div[7]/div/div/div/div", 
                                        document, 
                                        null, 
                                        XPathResult.FIRST_ORDERED_NODE_TYPE, 
                                        null
                                    ).singleNodeValue;
                                }
                                
                                if (popup) {
                                    // Look for any input in the popup
                                    var inputs = popup.querySelectorAll("input, [contenteditable='true']");
                                    if (inputs.length > 0) {
                                        inputs[0].value = "20";
                                        inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                                        inputs[0].dispatchEvent(new Event('change', { bubbles: true }));
                                        console.log("Set value to 20 using global search");
                                        return true;
                                    }
                                    
                                    // If no input found, try to set text on the div directly
                                    var divs = popup.querySelectorAll("div");
                                    for (var i = 0; i < divs.length; i++) {
                                        if (divs[i].textContent.trim() === "" || 
                                            /^[0-9]+$/.test(divs[i].textContent.trim())) {
                                            divs[i].textContent = "20";
                                            divs[i].dispatchEvent(new Event('input', { bubbles: true }));
                                            console.log("Set text content to 20");
                                            return true;
                                        }
                                    }
                                }
                                return false;
                            """)
                            logger.info("Attempted JavaScript brute force approach")

        except Exception as main_error:
            logger.error(f"All approaches to enter vote points failed: {main_error}")
            logger.warning("Continuing with the vote process anyway")

        # Take a screenshot to debug the issue
        try:
            logger.info("Taking screenshot of the vote screen")
            from utils import take_screenshot
            take_screenshot(driver, "vote_points_screen")
        except:
            pass

        time.sleep(2)  # Give time for any asynchronous operations to complete

        # Step 6: Click the "Vote" button in the popup to confirm
        logger.info("Confirming the vote")
        confirm_vote_xpath = "/html/body/div[7]/div/div/div/div/button"
        confirm_button = driver.find_element(By.XPATH, confirm_vote_xpath)
        driver.execute_script("arguments[0].click();", confirm_button)
        time.sleep(config.WAIT_SHORT)
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