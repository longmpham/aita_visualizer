import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def take_screenshot(url):
    # Start a new Chrome browser instance
    browser = webdriver.Chrome()

    # Navigate to the URL
    browser.get(url)
    browser.maximize_window()

    # Wait for the element to be visible
    post_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="t3_137ua7v"]')))

    # Take a screenshot of the element
    screenshot = post_element.screenshot_as_png

    # Save the screenshot to a file
    screenshot_folder = os.path.join(os.getcwd(), 'resources', 'screenshots')
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)
    screenshot_path = os.path.join(screenshot_folder, 'screenshot.png')
    with open(screenshot_path, 'wb') as f:
        f.write(screenshot)

    # Close the browser
    browser.quit()

    return screenshot_path
