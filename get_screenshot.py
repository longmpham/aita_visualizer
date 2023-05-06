import os
import requests
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

used_numbers = []

def get_post_screenshot(url):
    # Start a new Chrome browser instance
    browser = webdriver.Chrome()

    # Navigate to the URL
    browser.get(url)
    browser.maximize_window()

    # Wait for the element to be visible
    post_element = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/shreddit-app/div/div[2]/shreddit-post')))

    # Take a screenshot of the element
    screenshot = post_element.screenshot_as_png

    # Save the screenshot to a file
    screenshot_folder = os.path.join(os.getcwd(), 'resources', 'screenshots')
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)
    screenshot_path = os.path.join(screenshot_folder, 'screenshot_post.png')
    with open(screenshot_path, 'wb') as f:
        f.write(screenshot)

    # Close the browser
    browser.quit()

    return screenshot_path


def get_comment_screenshot(url, max_num_of_comments=3):

    def get_new_comment_id():
        global used_numbers
        new_comment_id = random.randint(3, 10)
        while new_comment_id in used_numbers:
            new_comment_id = random.randint(3, 10)
        used_numbers.append(new_comment_id)
        return new_comment_id

    url_json = url + ".json"
    max_num_of_comments = max_num_of_comments
    comment_id = 2  # start at 2, the 0,1 are bots.
    # get the url data from the url given
    response = requests.get(url_json, headers={'User-agent': 'Mozilla/5.0'})
    data = response.json()
    comments_data = data[1]['data']['children']
    # print(comments_data)
    # comments_list = [x['data']['body'] if x['data'][''] for x in comments_data]

    # Start a new Chrome browser instance
    browser = webdriver.Chrome()

    # Navigate to the URL
    browser.get(url)
    browser.maximize_window()

    # Scroll down by n x 1000 pixels
    for i in range(3):
        browser.execute_script("window.scrollBy(0, 1000)")
        time.sleep(3)

    for i in range(max_num_of_comments):
        # Get a comment number and the comment post
        # comment_id += 1  # for the top n comments
        comment_id = get_new_comment_id()
        post_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located(
            (By.XPATH, f'//*[@id="comment-tree"]/shreddit-comment[{comment_id}]')))

        # Take a screenshot of the element
        screenshot = post_element.screenshot_as_png

        # Save the screenshot to a file
        screenshot_folder = os.path.join(
            os.getcwd(), 'resources', 'screenshots')
        if not os.path.exists(screenshot_folder):
            os.makedirs(screenshot_folder)
        screenshot_path = os.path.join(
            screenshot_folder, f'screenshot_comment_{i+1}.png')
        with open(screenshot_path, 'wb') as f:
            f.write(screenshot)

        time.sleep(1)

    # Close the browser
    browser.quit()
    return screenshot_path


# get_comment_screenshot(
#     "https://www.reddit.com/r/AmItheAsshole/comments/138csc5/wibta_for_spraying_some_kid_with_my_garden_hose/", 3)
