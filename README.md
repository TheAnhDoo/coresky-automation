# Coresky Automation

Automated browser automation for Coresky tasks using Selenium and Python.

## Requirements

- Python 3.x
- Chrome/Chromium browser
- ChromeDriver
- MetaMask extension

## Setup

1. Install system dependencies:
```bash
sudo apt update
sudo apt install -y python3 python3-pip chromium-browser chromium-chromedriver
```

2. Install Python dependencies:
```bash
pip3 install selenium psutil
```

3. Download MetaMask extension (.crx file) and place it in the `coresky` directory

4. Create required directories:
```bash
mkdir -p coresky/browser-tools
mkdir -p coresky/screenshots
```

## Usage

Run the automation:
```bash
cd coresky
python3 multiprocessing_browser.py
```

## Configuration

Edit `config.py` to modify:
- MetaMask settings
- Coresky URLs
- Wait times
- Other automation parameters

## Logs

Logs are saved in:
- `automation_multi.log` - Main automation log
- `automation.log` - Single instance log 