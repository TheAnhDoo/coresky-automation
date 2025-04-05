# Coresky Automation

This project automates MetaMask wallet creation and interaction with the Coresky platform to perform daily tasks.

## Project Structure

- `main.py` - Main entry point that orchestrates the complete automation process
- `metamask.py` - Handles MetaMask extension setup, wallet creation, and connection
- `coresky.py` - Manages Coresky website interactions (check-in, voting, etc.)
- `utils.py` - Contains utility functions for browser automation
- `config.py` - Centralized configuration settings

## Requirements

- Python 3.7+
- Selenium WebDriver
- Chrome Browser
- ChromeDriver matching your Chrome version

## Installation

1. Place the MetaMask extension (.crx file) in the project root directory
2. Download the appropriate ChromeDriver for your Chrome version and place it in the `browser-tools/chromedriver_v134/chromedriver-win64/` directory (or update the path in `config.py`)
3. Install the required Python packages:

```bash
pip install selenium
```

## Usage

To run a single automation cycle:

```bash
python main.py
```

To run multiple cycles:

```bash
python main.py --cycles=3
```

To enable debug mode with more verbose logging:

```bash
python main.py --debug
```

## Configuration

All configuration settings are in `config.py`. Some important settings:

- `METAMASK_PASSWORD`: Password for creating MetaMask wallets
- `CORESKY_URL`: URL of the Coresky website
- `MEME_PROJECT_NAME`: Name of the meme project to vote for
- `MEME_VOTE_POINTS`: Number of points to allocate in voting
- `DEVELOPMENT_MODE`: Enable developer tools for debugging
- `KEEP_BROWSER_OPEN`: Keep browser open after completion
- `TAKE_SCREENSHOTS`: Enable screenshot capture during automation

## Troubleshooting

If the automation fails:

1. Check the `automation.log` file for error messages
2. Look at captured screenshots in the `screenshots` directory
3. Try running with `--debug` for more detailed logs
4. Ensure your ChromeDriver version matches your Chrome browser version
5. Make sure the MetaMask extension (.crx file) is valid

## Advanced Usage

To create a custom automation script using these modules:

```python
import logging
from selenium import webdriver
import metamask
import coresky
import config

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize the browser
driver = webdriver.Chrome()

# Set up MetaMask wallet
metamask.setup_metamask_wallet(driver)

# Connect to Coresky
metamask.connect_metamask_to_coresky(driver, config.CORESKY_URL)

# Perform check-in
coresky.perform_coresky_checkin(driver)

# Vote for a meme project
coresky.vote_for_meme_project(driver, "ProjectName", "10")

# Clean up
driver.quit()
``` 