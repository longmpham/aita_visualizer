import os
import requests
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import TimeoutException
import json
from datetime import datetime

# Path to the ublock extension file (.crx or .zip)
adblocker_path = "C:\\Users\\longp\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions\\cjpalhdlnbpafiamejdnhcphjbkeiagm\\1.49.2_0.crx"

chrome_options = ChromeOptions()
chrome_options.add_argument(f"--window-size={int(1920/3)},{int(1080)}")
chrome_options.add_extension(adblocker_path)
chrome_options.add_argument('--disable-notifications')
# chrome_options.add_argument("--headless")

def format_date(date_string):
    # Convert the string to a datetime object
    date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f%z")
    
    # Format the date as Month.Day.Year
    formatted_date = date_obj.strftime("%b.%d.%Y")
    
    return formatted_date

def save_json(post, file_name):
    with open(file_name, "w") as outfile:
        # Write the JSON data to the file with indentation for readability
        json.dump(post, outfile, indent=4)

def print_json(json_object):
    print(json.dumps(json_object, indent=2))

def take_screenshot(screenshot, folder_name, file_name):
    # Save the screenshot to a file
    screenshot_folder = os.path.join(os.getcwd(), 'resources', 'screenshots', folder_name)
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)
    screenshot_path = os.path.join(screenshot_folder, file_name)
    with open(screenshot_path, 'wb') as f:
        f.write(screenshot)
        print(f"took screenshot: {screenshot_path}")
    return screenshot_path

def get_all_posts(base_url, max_posts):
    # Start a new Chrome browser instance
    browser = webdriver.Chrome(options=chrome_options)

    # Navigate to the base url
    browser.get(base_url)
    # browser.execute_script("document.body.style.zoom='125%'")
    # browser.maximize_window()

    # Save the url and path of the images and the url to the main post
    posts = []    
    time.sleep(5) # 
    
    counter = 0
    i = 2
    while counter < max_posts:
        post_data = {
            "url": "",
            "screenshot_path": "",
        }
        try:
            # main post
            post_path_base = f"/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[4]/div[1]/div[4]/div[{i}]/div/div"
            post_title_element = WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.XPATH, post_path_base)))

            # post url
            post_url_element = post_path_base + "/div[3]/div[2]/div[1]/a"  # this is the url link where the href exists for the post.
            post_url_element = WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.XPATH, post_url_element)))
            post_url = post_url_element.get_attribute("href")

            # Take a screenshot of the element
            screenshot = post_title_element.screenshot_as_png
            screenshot_file_name = f'screenshot_title_{counter}.png'
            screenshot_folder_name = f'post_{counter}'
            screenshot_path = take_screenshot(screenshot, screenshot_folder_name, screenshot_file_name)

            # save path and url
            post_data["url"] = str(post_url)
            post_data["screenshot_path"] = str(screenshot_path)

            # Add the post_data to your list or perform any desired operations
            counter += 1
            i += 1
        except TimeoutException:
            i += 1 # invalid post or not found, go to next
            continue



        # Break the loop if the desired number of successful iterations is reached
        if counter == max_posts:
            break
            
        posts.append(post_data)
        
    # print(post)

    # Close the browser
    browser.quit()

    return posts

def get_post_data(posts, max_num_comments=3):

    # Start a new Chrome browser instance
    browser = webdriver.Chrome(options=chrome_options)
    post_data_list = []
    for i, post in enumerate(posts):
        base_url = post["url"]

        # Navigate to the base url
        browser.get(base_url)
        # browser.execute_script("document.body.style.zoom='125%'")
        # browser.maximize_window()

        post_data = {
            "title": "",
            "author": "",
            "body": [],
            "ups": 0,
            "num_comments": 0,
            "date": "",
            "comments": {},
            "screenshot_path": "",
        }
        # comments = {
        #     "author": "",
        #     "ups": "",
        #     "comments": [],
        #     "screenshot_path": [],
        # }
        
        time.sleep(5) # 

        # main post
        post_path_base = '/html/body/shreddit-app/div/div[2]/shreddit-post'
        post_main = WebDriverWait(browser, 70).until(
        EC.visibility_of_element_located((By.XPATH, post_path_base)))

        # details of main post
        post_title = post_main.get_attribute("post-title")
        post_author = post_main.get_attribute("author")
        post_ups = post_main.get_attribute("score")
        post_num_comments = post_main.get_attribute("comment-count")
        post_date = post_main.get_attribute("created-timestamp")
        
        # main post body
        p_elements = post_main.find_elements(By.XPATH, ".//p")
        # print(len(p_elements))
        
        # get all <p> elements found in the body block from the main post
        full_post_body = []
        for j, p_element in enumerate(p_elements):
            try:
                # inside the comment shreddit post, get the comment body
                post_main_line_path = post_path_base + f"/div[3]/div[1]/p[{j}]"
                post_main_line = WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.XPATH, post_main_line_path)))
                full_post_body.append(post_main_line.text)
                # print(post_comment_line.text)
            except TimeoutException:
                continue
        
        # Take a screenshot of the main post
        screenshot = post_main.screenshot_as_png
        screenshot_file_name = f'screenshot_post.png'
        screenshot_folder_name = f'post_{i}'
        screenshot_path_post = take_screenshot(screenshot, screenshot_folder_name, screenshot_file_name)
        
        # save path and url
        post_data["title"] = str(post_title)
        post_data["author"] = str(post_author)
        post_data["body"] = full_post_body
        post_data["ups"] = int(post_ups)
        post_data["num_comments"] = int(post_num_comments)
        post_data["date"] = format_date(str(post_date))
        post_data["screenshot_path"] = str(screenshot_path_post)
        
        # get the # of comments from the post. The first 2 comments are usually mod/bot posts
        for j in range(2,max_num_comments+2):
            comments = {
                "author": "",
                "ups": "",
                "comments": [],
                "screenshot_path": [],
                "date": "",
            }
            base_comment_path = f"/html/body/shreddit-app/div/div[2]/faceplate-batch/faceplate-tracker/shreddit-comment-tree/shreddit-comment[{j}]"
            # shreddit-comments look like this:
            # /html/body/shreddit-app/div/div[2]/faceplate-batch/faceplate-tracker/shreddit-comment-tree/shreddit-comment[2]    
            # /html/body/shreddit-app/div/div[2]/faceplate-batch/faceplate-tracker/shreddit-comment-tree/shreddit-comment[3]
            # /html/body/shreddit-app/div/div[2]/faceplate-batch/faceplate-tracker/shreddit-comment-tree/shreddit-comment[4]
            # p tags in the comment look like this
            # /html/body/shreddit-app/div/div[2]/faceplate-batch/faceplate-tracker/shreddit-comment-tree/shreddit-comment[2]/div[2]/div/p[1]
            # /html/body/shreddit-app/div/div[2]/faceplate-batch/faceplate-tracker/shreddit-comment-tree/shreddit-comment[2]/div[2]/div/p[2]
            
            # get the main comment shreddit post    
            post_comment = WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.XPATH, base_comment_path)))
            
            # get comment data
            post_comment_author = post_comment.get_attribute("author")
            post_comment_ups = post_comment.get_attribute("score")
            
            # get comment date
            comment_date_path = base_comment_path + "/div[1]/faceplate-timeago/time"
            post_comment_date_element = WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.XPATH, comment_date_path)))
            post_comment_date = post_comment_date_element.get_attribute("datetime")
            
            # Take a screenshot of the shreddit comment
            screenshot = post_comment.screenshot_as_png
            screenshot_file_name = f'screenshot_comment_{j}.png'
            screenshot_folder_name = f'post_{i}'
            screenshot_path_comment = take_screenshot(screenshot, screenshot_folder_name, screenshot_file_name)
                    

            # Count the number of p elements in the div
            p_elements = post_comment.find_elements(By.XPATH, ".//p")
            # print(len(p_elements))
            
            # get all <p> elements found in each comment block from the commenter
            full_comment = []
            for k, p_element in enumerate(p_elements):
                try:
                    # inside the comment shreddit post, get the comment body
                    post_comment_line_path = base_comment_path + f"/div[2]/div/p[{k}]"
                    if post_comment_line_path is None:
                        post_comment_line_path = base_comment_path + "/div[2]/div/p/text()"
                    post_comment_line = WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.XPATH, post_comment_line_path)))
                    full_comment.append(post_comment_line.text)
                    # print(post_comment_line.text)
                except TimeoutException:
                    continue
            
            print(full_comment)
            # add into post 
            comments["author"] = post_comment_author
            comments["ups"] = int(post_comment_ups)
            comments["comments"] = full_comment
            comments["screenshot_path"] = str(screenshot_path_comment)
            comments["date"] = format_date(str(post_comment_date))
            # print(comments)
            # add the comments into the full post
            post_data["comments"] = comments
            
        # finally, add the post to a list and send it off
        print(post_data)
        post_data_list.append(post_data)
        
    # time.sleep(0.5)
    save_json(post_data_list, "all_posts.json")
    # Close the browser
    browser.quit()

    return post_data_list





def get_post_screenshot2(url):
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

# url = "https://www.reddit.com/r/AskReddit/top"
url = "https://www.reddit.com/r/AmItheAsshole/top"
# post_url = "https://www.reddit.com/r/AmItheAsshole/comments/14c525u/aita_for_grounding_my_son_after_he_told_his/"
max_posts = 10

start_time = time.time()

posts = get_all_posts(url, max_posts)
print(posts)
print("done getting posts")
# get_post_screenshot(urls[0])
full_posts = get_post_data(posts, 3)
print(full_posts)

end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

# Print the elapsed time
print(f"Processing time: {elapsed_time} seconds")