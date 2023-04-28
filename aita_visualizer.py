import numpy as np
import requests
import time
import json
import pyttsx3
import re
from datetime import datetime, timedelta
from moviepy.editor import *
from gtts import gTTS
import string
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


acronyms_dict = {
    "AITA": "Am I the A-Hole",
    "BTW": "By the Way",
    "OMG": "Oh My God",
    "HVAC": "Heating, Ventilation, Air Conditioning",
    "YTA": "You're the A-Hole",
    "YWBTA": "You Would Be the A-Hole",
    "NTA": "Not the A-Hole",
    "YWNBTA": "You Would Not be the A-Hole",
    "ESH": "Everyone Sucks Here",
    "NAH": "No A-Holes Here",
    "AH": "A-Hole",
    "asshole": "A-Hole"
    # add more acronyms here if needed
}

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
            "author": comment["data"]["author"],
            "comment": comment["data"]["body"],
            "ups": comment["data"]["ups"],
            "utc_timestamp": comment["data"]["created_utc"],
            "relative_time": utc_to_relative_time(comment["data"]["created_utc"]),
            "date_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment["data"]["created_utc"]))
        })
    return comments

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
        author = post["data"]["author"]
        ups = post["data"]["ups"]
        utc_timestamp = post["data"]["created_utc"]
        url = post["data"]['url']
        utc_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(utc_timestamp))
        posts.append({
            "title": title,
            "selftext": selftext,
            "author": author,
            "ups": ups,
            "utc_timestamp": utc_timestamp,
            "relative_time": utc_to_relative_time(utc_timestamp),
            "url": url,
            "date_time": utc_time,
        })
    print(f"finished getting posts from {url}")
    return posts

def get_specific_post(posts, index):
    post = posts[index]
    # print_post(posts, index)
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
    merged_post = post
    merged_post["comments"] = comments
    save_json(merged_post, "post.json")
    return merged_post

def save_json(post, file_name="post.json"):
    file_name = file_name
    with open(file_name, "w") as outfile:
        # Write the JSON data to the file with indentation for readability
        json.dump(post, outfile, indent=4)

def print_json(json_object):
    print(json.dumps(json_object, indent=2))

def text_to_speech_pyttsx3(post, output_file="post-text.mp3"):
    text = post
    if isinstance(post, dict):
        text = post["title"] + post["selftext"]
    output_file = output_file
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    engine.setProperty('volume', 1)
    engine.setProperty('voice', engine.getProperty('voices')[1].id)
    engine.save_to_file(text, output_file)
    engine.runAndWait()
    return output_file

def text_to_speech_gtts(post):
    text = post["selftext"]
    output_file = "post-text.mp3"
    tts = gTTS(text, lang='en')
    tts.save(output_file)
    return output_file

def format_text_json(post):
    global acronyms_dict
    formatted_post = {}
    for key, val in post.items():
        if key == 'comments':
            formatted_comments = []
            for comment in val:
                formatted_comment = {}
                for comment_key, comment_val in comment.items():
                    if comment_key == 'comment':
                        for word in comment_val.split():
                            if word in acronyms_dict:
                                comment_val = comment_val.replace(word, acronyms_dict[word])                        
                        formatted_comment_val = re.sub(r'http\S+', '', comment_val) # Remove links from comment text
                        formatted_comment_val = re.sub(r'(?<=[a-z., ]{2})\n(?!\n)', '', formatted_comment_val) # Remove mid-sentence newline characters
                        formatted_comment[comment_key] = formatted_comment_val
                    elif comment_key == 'author':
                        formatted_comment[comment_key] = comment_val
                formatted_comments.append(formatted_comment)
            formatted_post[key] = formatted_comments
        elif key in ['title', 'selftext']:
            # Find and replace all keys from custom dictionary in the text
            for word in val.split():
                if word in acronyms_dict:
                    val = val.replace(word, acronyms_dict[word])
            formatted_val = re.sub(r'http\S+', '', val) # Remove links from selftext
            formatted_val = re.sub(r'(?<=[a-z., ]{2})\n(?!\n)', '', formatted_val) # Remove mid-sentence newline characters
            formatted_post[key] = formatted_val
        else:
            formatted_post[key] = val
    save_json(formatted_post, "clean_post.json")
    return formatted_post

def format_text(post):
    post_author = post["author"]
    post_title = post["title"]
    post_body = post["selftext"]
    comments = post["comments"] # list of dict
    post_formatted = "Redditor " + post_author + " wrote:\n" \
        + post_title + " " + post_body
    for comment in comments:
        post_formatted += "\n\n" + comment["author"] + " wrote:\n" + comment["comment"]
    return post_formatted

def createClip(post, mp3_file="post-text.mp3"):

    def create_post_text_for_video(post, audio_duration):
        post_body = post        
        total_words = len(post_body.split())
        wps_from_audio = total_words / audio_duration

        # Split the text into a list of paragraphs
        paragraph_list = post_body.split("\n\n")
        text_clips = []
        time = 0
        for i, text in enumerate(paragraph_list):
            num_words = len(text.split())
            duration = (num_words / wps_from_audio)
            text_clip = TextClip(text, font=font, fontsize=fontsize, color=color, bg_color=bg_color, align='West', method='caption', size=(mobile_text_size[0],None))
            # text_clip_pos = lambda t: (0, -5*i*t) # used to move text upwards
            # text_clip = text_clip.set_pos(text_clip_pos) # used to move text upwards
            text_clip = text_clip.set_start(time).set_pos('center').set_duration(duration).set_opacity(opacity)
            text_clips.append(text_clip)
            time += duration

        # Add the comments in snippets here
        # for comment in comments:
        #     formatted_comment = comment["author"] + " wrote: " + comment["comment"] + "\n\n"
        #     num_words = len(text.split())
        #     duration = 5 # 5 seconds per comment
        #     text_clip = TextClip(formatted_comment, font=font, fontsize=fontsize, color=color, bg_color=bg_color, align='West', method='caption', size=mobile_text_size)
        #     text_clip = text_clip.set_start(time).set_pos('center').set_duration(duration).set_opacity(opacity)
        #     text_clips.append(text_clip)
        #     time += duration

        ending_comments =  \
            "Comment what you think!" + "\n" + \
            "YTA = You're the A-hole" + "\n" + \
            "YWBTA = You Would Be the A-hole" + "\n" + \
            "NTA = Not the A-hole" + "\n" + \
            "YWNBTA = You Would Not be the A-hole" + "\n" + \
            "ESH = Everyone Sucks Here" + "\n" + \
            "NAH = No A-holes Here" + "\n" + \
            "INFO = Not Enough Info"

        ending_comments_clip = TextClip(ending_comments, font=font, fontsize=fontsize+4, color=color, bg_color=bg_color, align='West', method='caption', size=mobile_text_size)
        ending_comments_clip = ending_comments_clip.set_start(time).set_pos('center').set_duration(10)
        text_clips.append(ending_comments_clip)

        return text_clips

    def create_post_text_for_video_scroll(post, audio_duration):
        post_full = post
        text_clips = []

        # generate the full post text clip
        text_clip = TextClip(post_full, font=font, fontsize=fontsize, color=color, bg_color=bg_color, align='West', method='caption', size=(mobile_text_size[0],None))
        text_clip = text_clip.set_duration(audio_duration).set_opacity(opacity)
        text_clip_pos = lambda t: (0, 200-10*t) # used to move text upwards
        text_clip = text_clip.set_pos(text_clip_pos) # used to move text upwards
        text_clips.append(text_clip)

        # generate the ending credits text clip
        ending_comments =  \
            "Comment what you think!" + "\n" + \
            "YTA = You're the A-hole" + "\n" + \
            "YWBTA = You Would Be the A-hole" + "\n" + \
            "NTA = Not the A-hole" + "\n" + \
            "YWNBTA = You Would Not be the A-hole" + "\n" + \
            "ESH = Everyone Sucks Here" + "\n" + \
            "NAH = No A-holes Here" + "\n" + \
            "INFO = Not Enough Info"

        ending_comments_clip = TextClip(ending_comments, font=font, fontsize=fontsize+4, color=color, bg_color=bg_color, align='West', method='caption', size=mobile_text_size)
        ending_comments_clip = ending_comments_clip.set_start(audio_duration).set_pos('center').set_duration(10)
        text_clips.append(ending_comments_clip)

        return text_clips
    
    post = format_text_json(post)
    post_full = format_text(post)
    screenshot_file = ["screenshot.png"] # in a list since we're just using still images.
    video_files = "sea.mp4"
    # todo: replace image with a video?
    mp4_file = "Top AITA of the Day.mp4"
    width = 720
    height = int(width*9/16) # 16/9 screen
    video_size = width,height
    mobile_video_size = height,width
    text_size = (int(video_size[0]), int(video_size[1]*0.75)) # 16:9
    mobile_text_size = (int(video_size[1]), int(video_size[0]*0.75)) # 9:16
    font='Arial'
    fontsize=18
    color='white'
    bg_color='black'
    opacity = 0.60
    audio_file = mp3_file



    audio = AudioFileClip(text_to_speech_pyttsx3(post_full, audio_file))
    # video = ImageSequenceClip(screenshot_file, fps=1)
    video = VideoFileClip(video_files).loop(duration=10)
    video = video.set_duration(audio.duration)
    video = video.resize(mobile_video_size)
    # text_clips = create_post_text_for_video(post_full, audio.duration)
    text_clips = create_post_text_for_video_scroll(post_full, audio.duration)
    background_clip = video.set_audio(audio)
    final_clip = CompositeVideoClip([background_clip, *text_clips], size=mobile_video_size)
    final_clip.write_videofile(mp4_file)
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
    # mp3file = text_to_speech_pyttsx3(combined_post)
    # mp3file = text_to_speech_gtts(combined_post) # I find this too slow... no way to change it
    mp4file = createClip(combined_post)

    # Anything extra... 
    # print_post(reddit_posts, post_num)
    # print_comments(comments)
    # print_json(combined_post)

if __name__ == "__main__":
    main()
