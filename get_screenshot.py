import os
import requests
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

used_numbers = []

def get_new_comment_id():
    global used_numbers
    new_comment_id = random.randint(3, 10)
    while new_comment_id in used_numbers:
        new_comment_id = random.randint(3, 10)
    used_numbers.append(new_comment_id)
    return new_comment_id

def get_title_screenshot(url):
    # Start a new Chrome browser instance
    browser = webdriver.Chrome()

    # Navigate to the URL
    browser.get(url)
    browser.maximize_window()

    # Wait for the element to be visible
    # //*[@id="post-title-t3_138vxuu"]
    # /html/body/shreddit-app/div/div[2]/shreddit-post/div[2]
    post_element = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/shreddit-app/div/div[2]/shreddit-post/div[2]')))

    # Take a screenshot of the element
    screenshot = post_element.screenshot_as_png

    # Save the screenshot to a file
    screenshot_folder = os.path.join(os.getcwd(), 'resources', 'screenshots')
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)
    screenshot_path = os.path.join(screenshot_folder, 'screenshot_title.png')
    with open(screenshot_path, 'wb') as f:
        f.write(screenshot)

    # Close the browser
    browser.quit()

    return screenshot_path

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

    # url_json = url + ".json"
    comment_id = 2  # start at 2, the 0,1 are bots.
    # get the url data from the url given
    # response = requests.get(url_json, headers={'User-agent': 'Mozilla/5.0'})
    # data = response.json()
    # comments_data = data[1]['data']['children']
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

def get_full_screenshot(url, max_num_of_comments=3):

    screenshots = {"comments": []} # initialize a list for the comments key

    # Start a new Chrome browser instance
    browser = webdriver.Chrome()

    # Navigate to the URL
    browser.get(url)
    # browser.maximize_window()
    browser.set_window_size(1080, 1920)

    # Get the title element
    post_title = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/shreddit-app/div/div[2]/shreddit-post/div[2]')))

    # Take a screenshot of the element
    screenshots["title"] = post_title.screenshot_as_png
    print("got screenshot of title")
    time.sleep(1)

    # Get the post element
    post_element = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/shreddit-app/div/div[2]/shreddit-post')))

    # Take a screenshot of the element
    screenshots["post"] = post_element.screenshot_as_png
    print("got screenshot of post body")

    time.sleep(1)

    # Scroll down to load some comments
    for i in range(3):
        browser.execute_script("window.scrollBy(0, 1000)")
        time.sleep(1)

    # Get the comment element(s)
    for i in range(max_num_of_comments):
        try:
            comment_id = get_new_comment_id() # gets random comment id from 2-24
            comment_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located(
                (By.XPATH, f'//*[@id="comment-tree"]/shreddit-comment[{comment_id}]')))

            # Take a screenshot of the element
            screenshots["comments"].append(comment_element.screenshot_as_png)
            print("got screenshot of post comments")

            time.sleep(2)
        except:
            print("couldn't get screenshot")

    # Save the screenshot to a file
    screenshot_folder = os.path.join(os.getcwd(), 'resources', 'screenshots')
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)

    screenshot_paths = []
    # Save title screenshot
    title_path = os.path.join(screenshot_folder, 'screenshot_title.png')
    screenshot_paths.append(title_path)
    with open(title_path, 'wb') as f:
        f.write(screenshots['title'])

    # Save post screenshot
    post_path = os.path.join(screenshot_folder, 'screenshot_post.png')
    screenshot_paths.append(post_path)
    with open(post_path, 'wb') as f:
        f.write(screenshots['post'])


    # Save comment screenshots
    comment_paths = []
    for i, comment in enumerate(screenshots['comments']):
        comment_path = os.path.join(screenshot_folder, f'screenshot_comment_{i}.png')
        comment_paths.append(comment_path)
        with open(comment_path, 'wb') as f:
            f.write(comment)   
    screenshot_paths.append(comment_paths)

    # Close the browser
    browser.quit()

    # print(screenshot_paths)
    return screenshot_paths

# get_comment_screenshot(
#     "https://www.reddit.com/r/AmItheAsshole/comments/138csc5/wibta_for_spraying_some_kid_with_my_garden_hose/", 3)
