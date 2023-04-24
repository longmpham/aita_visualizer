import numpy as np
import requests
import time
import json
import pyttsx3
import re
from datetime import datetime, timedelta
from moviepy.editor import *
from gtts import gTTS


acronyms_dict = {
    "AITA": "Am I the Asshole",
    "BTW": "By the Way",
    "OMG": "Oh My God",
    "HVAC": "Heating, Ventilation, Air Conditioning",
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
    merged_post = {}
    merged_post.update(post)
    merged_post["comments"] = comments
    return merged_post

def print_json(json_object):
    print(json.dumps(json_object, indent=2))

def text_to_speech_pyttsx3(post):
    text = post["title"] + post["selftext"]
    output_file = "post-text.mp3"
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

def format_text(post):
    # Explanation:
    # 
    # 1. Match a single character present in the list below [a-z]{2}. {2} Quantifier — Matches exactly 2 times.
    # 2. \n matches a line-feed (newline) character (ASCII 10)
    # 3. Negative Lookahead (?!\n). Assert that the Regex below does not match.
    # https://stackoverflow.com/questions/61150145/remove-line-breaks-but-not-double-line-breaks-python
    # formatted_text = text.replace("*", "")
    # formatted_text = re.sub(r'(?<=[a-z., ]{2})\n(?!\n)', '', formatted_text)
    # return formatted_text

    formatted_post = {}
    for key, val in post.items():
        if key == 'comments':
            formatted_comments = []
            for comment in val:
                formatted_comment = {}
                for comment_key, comment_val in comment.items():
                    if comment_key == 'comment':
                        formatted_comment_val = comment_val.replace("*", "")
                        formatted_comment_val = re.sub(r'(?<=[a-z., ]{2})\n(?!\n)', '', formatted_comment_val)
                        formatted_comment[comment_key] = formatted_comment_val
                    elif comment_key == 'author':
                        formatted_comment[comment_key] = comment_val
                formatted_comments.append(formatted_comment)
            formatted_post[key] = formatted_comments
        elif key in ['title', 'selftext']:
            formatted_val = val.replace("*", "")
            formatted_val = re.sub(r'(?<=[a-z., ]{2})\n(?!\n)', '', formatted_val)
            formatted_post[key] = formatted_val
        else:
            formatted_post[key] = val
    return formatted_post

def format_text2(post):
    global acronyms_dict
    formatted_post = {}
    for key, val in post.items():
        if key == 'comments':
            formatted_comments = []
            for comment in val:
                formatted_comment = {}
                for comment_key, comment_val in comment.items():
                    if comment_key == 'comment':
                        formatted_comment_val = comment_val.replace("*", "")
                        formatted_comment_val = re.sub(r'(?<=[a-z., ]{2})\n(?!\n)', '', formatted_comment_val)
                        formatted_comment[comment_key] = formatted_comment_val
                    elif comment_key == 'author':
                        formatted_comment[comment_key] = comment_val
                formatted_comments.append(formatted_comment)
            formatted_post[key] = formatted_comments
        elif key in ['title', 'selftext']:
            # Find and replace all acronyms in the text
            acronyms = re.findall(r'\b[A-Z]{2,}\b', val)
            for acronym in acronyms:
                acronym_upper = acronym.upper()
                if acronym_upper in acronyms_dict:
                    val = val.replace(acronym, acronyms_dict[acronym_upper])
                else:
                    acronyms_dict[acronym_upper] = acronym
                val = val.replace(acronym, acronym_upper)
            formatted_val = val.replace("*", "")
            formatted_val = re.sub(r'(?<=[a-z., ]{2})\n(?!\n)', '', formatted_val)
            formatted_post[key] = formatted_val
        else:
            formatted_post[key] = val
    return formatted_post

def createClip(mp3file, post):
    screenshot_file = ["screenshot.jpg"] # in a list since we're just using still images.
    mp4_file = "Top AITA of the Day.mp4"
    post = post
    width = 720
    height = int(width*9/16) # 16/9 screen
    video_size = width,height
    text_size = (int(video_size[0]*0.75), int(video_size[1]*0.75))
    font='Arial'
    fontsize=18
    color='white'
    bg_color='transparent'

    def create_post_text_for_video(post, total_tts_time):
        post_title = post["title"]
        post_body = post["selftext"]
        post_body = post_title + " " + post_body

        # Split the text into a list of paragraphs
        paragraph_list = post_body.split("\n\n")
        step = total_tts_time/len(paragraph_list) #each 15 sec: 0, 15, 30
        # wpm = 175
        # words_per_second = wpm / 60
        duration = step
        time = 0
        text_clips = []
        for text,i in zip(paragraph_list,range(0,len(paragraph_list))):
            text_clip = TextClip(text,font=font, fontsize=fontsize, color=color, bg_color='transparent', align='West', method='caption', size=text_size)
            text_clip = text_clip.set_start(time)
            text_clip = text_clip.set_pos('center').set_duration(duration)
            # text_clip = text_clip.set_pos('center').set_duration(3 if i==0 else duration)
            text_clips.append(text_clip)  
            time += step
            # time += 3 if i==0 else step
            # print(text_clip)

        return text_clips
        # return post_body

    def create_post_text_for_video2(post, total_tts_time):
        wpm = 190
        post_title = post["title"]
        post_body = post["selftext"]
        post_body = post_title + " " + post_body

        # Split the text into a list of paragraphs
        paragraph_list = post_body.split("\n\n")
        words_per_second = wpm / 60
        text_clips = []
        time = 0
        for i, text in enumerate(paragraph_list):
            num_words = len(text.split())
            duration = (num_words / words_per_second)
            # for acronym in acronyms_dict.keys():
            #     if acronym in text:
            #         print('check!')
            #         duration -= 2
            #         break
            print(duration)
            text_clip = TextClip(text, font=font, fontsize=fontsize, color=color, bg_color='transparent', align='West', method='caption', size=text_size)
            text_clip = text_clip.set_start(time).set_pos('center').set_duration(duration)
            text_clips.append(text_clip)
            time += duration

        return text_clips

    def create_comments_text_for_video(post):
        # comments = post["comments"]
        # formatted_comments = '\n'.join([comment['comment'] for comment in comments])
        # # print(formatted_comments)
        # return formatted_comments
    
        comments = post["comments"]
        formatted_comments = ""
        for comment in comments:
            formatted_comments += f"{comment['author']}:\n{comment['comment']}\n\n"
        
        formatted_comments = formatted_comments + "\n\n" +  "Comment what you think!" + "\n" + \
            "YTA = You're the Asshole" + " | " + \
            "YWBTA = You Would Be the Asshole" + " | " + \
            "NTA = Not the Asshole" + " | " + \
            "YWNBTA = You Would Not be the Asshole" + " | " + \
            "ESH = Everyone Sucks Here" + " | " + \
            "NAH = No Assholes Here" + " | " + \
            "INFO = Not Enough Info"
        return formatted_comments
    
    post = format_text2(post)

    audio = AudioFileClip(text_to_speech_pyttsx3(post))
    video = ImageSequenceClip(screenshot_file, fps=5)
    video.set_duration(audio.duration)
    audio_duration = int(audio.duration) + 5
    text_clips = create_post_text_for_video2(post, audio_duration)
    # Create a TextClip with the selftext
    # post_body_text_clip = TextClip(post_body, font=font, fontsize=fontsize, color=color, bg_color=bg_color, align="West", method='caption', size=video_size)
    # post_body_text_clip.set_duration(audio.duration) # add 5 seconds to the end of the clip to make sure it's the last thing in the video
    # post_body_text_clip.resize(video_size)

    # Create a composite video of text clips
    

    # Add the audio to the video
    background_clip = video.set_audio(audio)
    intermediate_clip = CompositeVideoClip([background_clip, *text_clips], size=video_size)
    # intermediate_clip.set_duration(audio_duration)
    # intermediate_clip.resize(video_size)

    # Add the comments section at the end of the video
    comments = create_comments_text_for_video(post)
    # comments = format_text(comments)
    comments_clip = TextClip(comments, font=font, fontsize=fontsize, color=color, bg_color=bg_color, align='West', method='caption', size=video_size)
    comments_clip = comments_clip.set_position("center", "center")
    comments_clip = comments_clip.set_start(audio.duration)
    comments_clip = comments_clip.set_end(audio.duration + 20)

    # final_clip = CompositeVideoClip([intermediate_clip, comments_clip])
    # print(intermediate_clip.duration)
    # final_duration = (int(comments_clip.duration) + int(intermediate_clip.duration))
    final_clip = CompositeVideoClip([intermediate_clip, comments_clip]).set_duration(audio.duration + 20) # play comments for 20s

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
    mp3file = text_to_speech_pyttsx3(combined_post)
    # mp3file = text_to_speech_gtts(combined_post) # I find this too slow...
    mp4file = createClip(mp3file, combined_post)

    # Anything extra... 
    # print_post(reddit_posts, post_num)
    # print_comments(comments)
    # print_json(combined_post)

if __name__ == "__main__":
    main()
