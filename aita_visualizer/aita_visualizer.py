import numpy as np
import requests
import time
import json
import pyttsx3
import re
from datetime import datetime, timedelta
from moviepy.editor import *
from gtts import gTTS
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
nltk.download('stopwords')
nltk.download('wordnet')

acronyms_dict = {
    "AITA": "Am I the Asshole",
    "BTW": "By the Way",
    "OMG": "Oh My God",
    "HVAC": "Heating, Ventilation, Air Conditioning",
    "YTA": "You're the Asshole",
    "YWBTA": "You Would Be the Asshole",
    "NTA": "Not the Asshole",
    "YWNBTA": "You Would Not be the Asshole",
    "ESH": "Everyone Sucks Here",
    "NAH": "No Assholes Here",
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
    print_post(posts, index)
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

    # clean it from weird crap with nltk
    # cleaned_post = clean_text_withnltk(merged_post)
    save_json(merged_post)
    return merged_post

def save_json(post):
    with open("post.json", "w") as outfile:
        # Write the JSON data to the file with indentation for readability
        json.dump(post, outfile, indent=4)

def print_json(json_object):
    print(json.dumps(json_object, indent=2))

def text_to_speech_pyttsx3(post):
    if isinstance(post, dict):
        text = post["title"] + post["selftext"]
    else:
        text = post
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
    global acronyms_dict
    formatted_post = {}
    for key, val in post.items():
        if key == 'comments':
            formatted_comments = []
            for comment in val:
                formatted_comment = {}
                for comment_key, comment_val in comment.items():
                    if comment_key == 'comment':
                        # Remove links from comment text
                        comment_val = re.sub(r'http\S+', '', comment_val)
                        formatted_comment_val = re.sub(r'(?<=[a-z., ]{2})\n(?!\n)', '', comment_val)
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
            # Remove links from selftext
            val = re.sub(r'http\S+', '', val)
            formatted_val = re.sub(r'(?<=[a-z., ]{2})\n(?!\n)', '', val)
            formatted_post[key] = formatted_val
        else:
            formatted_post[key] = val
        save_json(formatted_post)
    return formatted_post

def createClip(mp3file, post):

    def create_post_text_for_video(post, audio_duration):
        words_per_minute = 175 #225 seems like the sweet spot even though its set as 175...
        post_author = post["author"]
        post_title = post["title"]
        post_body = post["selftext"]
        comments = post["comments"] # list of dict
        words_per_second = words_per_minute / 60

        post_body = "Redditor " + post_author + " wrote:\n" \
            + post_title + " " + post_body
        text_to_speech_pyttsx3(post_body)

        total_words = len(post_body.split())
        print(total_words)
        wps_from_audio = total_words / audio_duration
        print(wps_from_audio)
        # Split the text into a list of paragraphs
        paragraph_list = post_body.split("\n\n")
        text_clips = []
        time = 0
        for i, text in enumerate(paragraph_list):
            # num_sentences = len(re.findall(r'\b[\w\s,]+\W\s', text))
            # print(num_sentences)
            num_words = len(text.split())
            # duration = (num_words / words_per_second) - (num_sentences*1.4) # THIS IS SO HARD....... WPM != AUDIO :(
            duration = num_words * wps_from_audio
            if(duration < 0): duration = 1
            text_clip = TextClip(text, font=font, fontsize=fontsize, color=color, bg_color=bg_color, align='West', method='caption', size=(mobile_text_size[0],None))
            # text_clip_pos = lambda t: (0, -5*i*t)
            # text_clip = text_clip.set_pos(text_clip_pos)
            # text_clip = text_clip.set_start(time).set_duration(duration).set_opacity(opacity)
            text_clip = text_clip.set_start(time).set_pos('center').set_duration(duration).set_opacity(opacity)
            text_clips.append(text_clip)
            time += duration

        # Split the text into a list of sentences instead
        # sentence_list = re.findall(r'\b[\w\s,]+\W\s', post_body)
        # x = 5 # set the number of sentences per sublist
        # sentence_sublists = [sentence_list[i:i+x] for i in range(0, len(sentence_list), x)]

        # text_clips = []
        # time = 0
        # for sublist in sentence_sublists:
        #     print(sublist)
        #     text = ''.join(sublist)
        #     num_words = len(text.split())
        #     # duration = (num_words / words_per_second) - (len(sublist)*1.45) # THIS IS SO HARD....... WPM != AUDIO :(
        #     duration = (num_words / words_per_second) # THIS IS SO HARD....... WPM != AUDIO :(
        #     if(duration < 0): duration = 1
        #     text_clip = TextClip(text, font=font, fontsize=fontsize, color=color, bg_color=bg_color, align='West', method='caption', size=mobile_text_size)
        #     text_clip = text_clip.set_start(time).set_pos('center').set_duration(duration).set_opacity(opacity)
        #     text_clips.append(text_clip)
        #     time += duration

        # Add the comments in snippets here
        for comment in comments:
            formatted_comment = comment["author"] + " wrote: " + comment["comment"] + "\n\n"
            num_sentences = len(re.findall(r'\b[\w\s,]+\W\s', formatted_comment)) + 1
            num_words = len(text.split())
            # duration = (num_words / words_per_second) - (num_sentences*1.45) # THIS IS SO HARD....... WPM != AUDIO :(
            duration = 5 # 5 seconds per comment
            text_clip = TextClip(formatted_comment, font=font, fontsize=fontsize, color=color, bg_color=bg_color, align='West', method='caption', size=mobile_text_size)
            text_clip = text_clip.set_start(time).set_pos('center').set_duration(duration).set_opacity(opacity)
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
        
        formatted_comments = formatted_comments + \
            "Comment what you think!" + "\n" + \
            "YTA = You're the Asshole" + " | " + \
            "YWBTA = You Would Be the Asshole" + " | " + \
            "NTA = Not the Asshole" + " | " + \
            "YWNBTA = You Would Not be the Asshole" + " | " + \
            "ESH = Everyone Sucks Here" + " | " + \
            "NAH = No Assholes Here" + " | " + \
            "INFO = Not Enough Info"
        return formatted_comments
    
    post = format_text(post)
    screenshot_file = ["screenshot.png"] # in a list since we're just using still images.
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
    opacity = 0.75
    ending_comments =  \
        "Comment what you think!" + "\n" + \
        "YTA = You're the Asshole" + "\n" + \
        "YWBTA = You Would Be the Asshole" + "\n" + \
        "NTA = Not the Asshole" + "\n" + \
        "YWNBTA = You Would Not be the Asshole" + "\n" + \
        "ESH = Everyone Sucks Here" + "\n" + \
        "NAH = No Assholes Here" + "\n" + \
        "INFO = Not Enough Info"

    audio = AudioFileClip(text_to_speech_pyttsx3(post))
    video = ImageSequenceClip(screenshot_file, fps=1)
    video = video.set_duration(audio.duration)
    video = video.resize(mobile_video_size)
    audio_duration = int(audio.duration)
    text_clips = create_post_text_for_video(post, audio_duration)

    # Add the audio to the video
    background_clip = video.set_audio(audio)
    intermediate_clip = CompositeVideoClip([background_clip, *text_clips], size=mobile_video_size)
    ending_comments_clip = TextClip(ending_comments, font=font, fontsize=fontsize+4, color=color, bg_color=bg_color, align='West', method='caption', size=mobile_text_size).set_start(intermediate_clip.duration).set_end(intermediate_clip.duration + 5)
    final_clip = CompositeVideoClip([intermediate_clip, ending_comments_clip], size=mobile_video_size)
    final_clip.write_videofile(mp4_file)
    return mp4_file

def clean_text_withnltk(data):
    title = data["title"]
    selftext = data["selftext"]
    comments = data["comments"]
    # Tokenize the text
    tokens = word_tokenize(selftext)

    # Rejoin the tokens into a cleaned string
    cleaned_text = ' '.join(tokens)
    data["selftext"] = cleaned_text

    print(data)

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
    # mp3file = text_to_speech_gtts(combined_post) # I find this too slow... no way to change it
    mp4file = createClip(mp3file, combined_post)

    # Anything extra... 
    # print_post(reddit_posts, post_num)
    # print_comments(comments)
    # print_json(combined_post)

if __name__ == "__main__":
    main()
