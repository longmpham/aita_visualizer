import requests
import time
import json
import pyttsx3
from datetime import datetime, timedelta
from moviepy.editor import *

def utc_to_relative_time(utc_timestamp):
    now = datetime.utcnow()
    post_time = datetime.utcfromtimestamp(utc_timestamp)
    time_diff = now - post_time
    if time_diff < timedelta(minutes=1):
        return 'just now'
    elif time_diff < timedelta(hours=1):
        minutes = int(time_diff.total_seconds() / 60)
        return f'{minutes} minutes ago'
    elif time_diff < timedelta(days=1):
        hours = int(time_diff.total_seconds() / 3600)
        return f'{hours} hours ago'
    else:
        days = time_diff.days
        return f'{days} days ago'

def get_comments(url,max_num_of_comments=3):
    # print(url)
    url = url + ".json"
    max_num_of_comments = max_num_of_comments

    # get the url data from the url given
    response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
    data = response.json()
    comments_data = data[1]['data']['children']

    # get the post body data from data
    comments = []
    for index, comment in enumerate(comments_data[1:max_num_of_comments+1]):
        comments.append({
            "index": index+1,
            "comment": comment["data"]["body"],
            "author": comment["data"]["author"],
            "ups": comment["data"]["ups"],
            "utc_timestamp": comment["data"]["created_utc"],
            "relative_time": utc_to_relative_time(comment["data"]["created_utc"]),
        })

    return comments

    # using list comprehension...
    # comments_data = data[1]['data']['children'][1:num_comments+1]
    # comments = [comment['data']['body'] for comment in comments_data]
    # return comments

def print_comments(comments):
    for index, comment in enumerate(comments):
        print(
            "===================================================",
            "Index: " + str(comment["index"]),
            "Author: " + comment["author"],
            "Comment: " + comment["comment"],
            "Ups: " + str(comment["ups"]),
            "Relative-Time: " + str(comment["relative_time"]),
            sep='\n',
        )    
        # print("Comment #" + str(index+1) + ": " + comment)

def get_posts(url):
    
    # get all posts from the url given
    url = url
    response = requests.get(url, headers={"User-agent": "Mozilla/5.0"})
    data = response.json()

    # create a list of dictionaries (reddit posts) from the data
    posts = []
    for post in data["data"]["children"]:
        title = post["data"]["title"]
        selftext = post["data"]["selftext"]
        ups = post["data"]["ups"]
        utc_timestamp = post["data"]["created_utc"]
        url = post["data"]['url']
        utc_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(utc_timestamp))
        posts.append({
            "title": title,
            "selftext": selftext,
            "ups": ups,
            "utc_timestamp": utc_timestamp,
            "relative_time": utc_to_relative_time(utc_timestamp),
            "url": url,
            "date_time": utc_time,
        })

        # test printing 
        # print(f'
        #   Title: {title}\n
        #   Selftext: {selftext}\n
        #   Ups: {ups}\n
        #   UTC time: {utc_time} UTC\n
        #   Relative time: {relative_time} ago\n
        #   URL: {url}\n'
        # )
    return posts

def get_specific_post(posts, index):
    post = posts[index]
    return post

def print_post(posts, index=0):
    post = posts[index]
    print(
        "Title: " + post["title"],
        "Selftext: " + post["selftext"],
        "Ups: " + str(post["ups"]),
        # "Utc-Timestamp: " + str(post["utc_timestamp"]),
        "Relative-Time: " + str(post["relative_time"]),
        "Date/Time: " + str(post["date_time"]),
        "Url: " + post["url"],
        sep='\n',
    )

def print_all_posts(posts):
    for post in posts[0]:
        print(
            "Title: " + post["title"],
            "Selftext: " + post["selftext"],
            "Ups: " + str(post["ups"]),
            # "Utc-Timestamp: " + str(post["utc_timestamp"]),
            "Relative-Time: " + str(post["relative_time"]),
            "Date/Time: " + str(post["date_time"]),
            "Url: " + post["url"],
            sep='\n',
        )

def get_num_of_posts(posts):
    print(len(posts))
    return len(posts)

def combine_post_comments(post,comments):
    # what is the type of post and comments?
    # print(type(post)) # dict
    # print(type(comments)) # list of dict
    merged_post = {}
    merged_post.update(post)
    merged_post["comments"] = comments
    return merged_post

def print_json(json_object):
    print(json.dumps(json_object, indent=2))

def text_to_speech(post):
    text = post["selftext"]
    output_file = "post-text.mp3"
    engine = pyttsx3.init()
    engine.setProperty('rate', 200)
    engine.setProperty('volume', 1)
    engine.setProperty('voice', engine.getProperty('voices')[1].id)
    engine.save_to_file(text, output_file)
    engine.runAndWait()
    return output_file

def createClip(screenshotFile, mp3file):
    # todo: create a text overlay on the screenshot 
    # for subtitleson the screen
    mp4file = "post.mp4"
    audio = AudioFileClip(mp3file)
    video = ImageSequenceClip(screenshotFile, fps=5).set_duration(audio.duration)
    # video = ColorClip((640, 480), color=(255, 255, 255))
    final_clip = video.set_audio(audio)
    final_clip.write_videofile(mp4file)
    return mp4file

def main():
    # 1.  Get all top posts from a subreddit
    # 2.  Get the comments from the top post
    # 3.  Combine the top post and the comments
    # 4.  Print the combined post
    # 5.  Convert the combined post to an mp3 file
    # 6.  Play the mp3 file

    url = "https://www.reddit.com/r/AmItheAsshole/top.json?t=day"
    reddit_posts = get_posts(url)
    post_num = 0 # first (top most post)
    reddit_post = get_specific_post(reddit_posts, post_num)
    # print_post(reddit_posts, post_num)
    num_of_comments = 3
    comments = get_comments(reddit_post['url'], num_of_comments)
    # print_comments(comments)
    combined_post = combine_post_comments(reddit_post, comments)
    print_json(combined_post)
    screenshotFile = ["screenshot.jpg"]    
    mp3file = text_to_speech(combined_post)
    mp4file = createClip(screenshotFile, mp3file)

if __name__=="__main__":
    main()