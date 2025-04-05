import os

# Base directories
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BROWSER_TOOLS_DIR = os.path.join(CURRENT_DIR, "browser-tools")
SCREENSHOTS_DIR = os.path.join(CURRENT_DIR, "screenshots")

# Create necessary directories
os.makedirs(BROWSER_TOOLS_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Browser paths
METAMASK_CRX_PATH = os.path.join(CURRENT_DIR, "MetaMask.crx")
SELECTORSHUB_CRX_PATH = os.path.join(CURRENT_DIR, "SelectorsHub.crx")
# CHROMEDRIVER_PATH = "/usr/bin/chromedriver"  # Using system-installed ChromeDriver
CHROMEDRIVER_PATH = os.path.join(BROWSER_TOOLS_DIR, "chromedriver")
# MetaMask settings
METAMASK_EXTENSION_ID = "nkbihfbeogaeaoehlefnkodbefgpgknn"
METAMASK_PASSWORD = "123123123"

# Coresky settings
CORESKY_URL = "https://www.coresky.com/tasks-rewards"
CORESKY_TASKS_URL = "https://www.coresky.com/tasks-rewards"
MEME_PROJECT_NAME = "kmoii"
MEME_VOTE_POINTS = "20"

# Wait times in seconds
WAIT_SHORT = 2
WAIT_MEDIUM = 5
WAIT_LONG = 10
DEFAULT_IMPLICIT_WAIT = 10
DELAY_BETWEEN_CYCLES = 30  # Delay between automation cycles

# Development settings
DEVELOPMENT_MODE = False  # Set to True to enable developer tools and other debug features
KEEP_BROWSER_OPEN = False  # Keep browser open after completion (useful for debugging)
TAKE_SCREENSHOTS = False  # Whether to take screenshots during the process

# Maximum attempts for retrying operations
MAX_CLICK_ATTEMPTS = 3
MAX_CONNECTION_ATTEMPTS = 3

# Create screenshots directory if it doesn't exist
if TAKE_SCREENSHOTS and not os.path.exists(SCREENSHOTS_DIR):
    try:
        os.makedirs(SCREENSHOTS_DIR)
    except:
        print(f"Warning: Could not create screenshots directory at {SCREENSHOTS_DIR}")
        TAKE_SCREENSHOTS = False 