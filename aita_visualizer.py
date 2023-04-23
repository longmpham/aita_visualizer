import numpy as np
import requests
import time
import json
import pyttsx3
import re
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


def get_comments(url, max_num_of_comments=3):
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
        utc_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(utc_timestamp))
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


def combine_post_comments(post, comments):
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

def format_text_to_fit_window(words):
    words = words.split()
    for i in range(7, len(words), 8):
        words[i] += '\n'
    return ' '.join(words)

def createClip(mp3file, post):
    screenshot_file = ["screenshot.jpg"]
    mp4_file = "post.mp4"
    post_body = post["selftext"]
    video_size = (1280, 720)
    # w = 720
    # h = w*9/16 # 16/9 screen
    # video_size = w,h

    # post_body = format_text_to_fit_window(post_body)
    # print(post_body)
    post_title = post["title"]
    post_body = post_title + "\n\n" + post_body
    post_body = post_body + "\n\n" +  "Comment what you think!" + "\n" + \
        "YTA = You're the Asshole" + " | " + \
        "YWBTA = You Would Be the Asshole" + " | " + \
        "NTA = Not the Asshole" + \
        "YWNBTA = You Would Not be the Asshole" + " | " + \
        "ESH = Everyone Sucks Here" + " | " + \
        "NAH = No Assholes Here" + " | " + \
        "INFO = Not Enough Info"
    
    comments = post["comments"]

    audio = AudioFileClip(mp3file)
    video = ImageSequenceClip(screenshot_file, fps=5)
    video.set_duration(audio.duration)
    
    # Create a TextClip with the selftext
    post_body_text_clip = TextClip(post_body, font='Arial', fontsize=18, color='white', bg_color='black', align="West", method='caption', size=video_size)
    post_body_text_clip.set_duration(audio.duration + 5) # add 5 seconds to the end of the clip to make sure it's the last thing in the video
    post_body_text_clip.resize(video_size)

    # Put everything together
    background_clip = video.set_audio(audio)
    final_clip = CompositeVideoClip([background_clip, post_body_text_clip], size=video_size).set_duration(audio.duration).resize(video_size)

    final_clip.write_videofile(mp4_file)
    # background_clip.write_videofile(mp4_file)
    return mp4_file

def main():
    # 1. Get all top posts from a subreddit
    # 2. Get the comments from the top post
    # 3. Combine the top post and the comments
    # 4. Print the combined post
    # 5. Convert the combined post to an mp3 file
    # 6. Convert the mp3 file to an mp4 file
    # 7. Add the post as a text overlay on top of the video
    # 8. When the video ends, add the comments
    # todo: 9. Autologin to YT, post the video

    # Variables to choose from...
    url = "https://www.reddit.com/r/AmItheAsshole/top.json?t=day"
    post_num = 0  # first (top most post) (usually <25 posts)
    num_of_comments = 3

    # The logic...
    reddit_posts = get_posts(url)
    reddit_post = get_specific_post(reddit_posts, post_num)
    comments = get_comments(reddit_post['url'], num_of_comments)
    combined_post = combine_post_comments(reddit_post, comments)
    mp3file = text_to_speech(combined_post)
    mp4file = createClip(mp3file, combined_post)

    # Anything extra... 
    # print_post(reddit_posts, post_num)
    # print_comments(comments)
    # print_json(combined_post)



if __name__ == "__main__":
    main()
