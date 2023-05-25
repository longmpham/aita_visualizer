import os
import numpy as np
import requests
import time
import json
import pyttsx3
import re
import random
from datetime import datetime, timedelta
from moviepy.editor import *
from gtts import gTTS
import unicodedata
# from youtube_uploader_selenium import YouTubeUploader
# from selenium.webdriver.common.by import By
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks
from pydub.silence import split_on_silence
from moviepy.video.tools.subtitles import SubtitlesClip
from get_screenshot import get_full_screenshot



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
    "asshole": "A-Hole",
    "fuck": "F",
    "fucking": "F-ing",
    "WIBTA": "would I be the A-Hole",
    "AITA?": "Am I The A-Hole?"
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

def format_meta_text(post):
    
    post_author = post["author"]
    post_title = post["title"]
    post_body = post["selftext"]
    post_ups = post["ups"]
    post_date = post["date_time"]

    post_meta = "AITA\n" + str(post_ups) + " ups\n" + post_author + " wrote:\n" + post_title + "\n\n" + post_date
    post_meta_json = {
        "title": "Top AITA of the Day | " + post_title,
        "description": post_title + "wrote: " + post_body,
        "tags": ["Reddit", "AITA"],
        # "schedule": "",
    }
    save_json(post_meta_json, file_name="yt_meta_data.json")
    return post_meta

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
    clean_json_file(input_file="clean_post.json", output_file="super_cleaned_post.json")
    return formatted_post

def clean_json_file(input_file, output_file):
    def clean_text(text):
        # Convert to string if input is not already a string
        if not isinstance(text, str):
            text = str(text)

        # Remove Unicode characters
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

        # Remove newlines ("\n")
        text = re.sub(r"\n+", " ", text)
        
        # # Remove Unicode characters
        # text = re.sub(r"\\u\d{4}", "", text)
        
        # Remove other escape characters
        text = re.sub(r"\\[^\w\s]", "", text)
        
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        
        return text.strip()

    # Load the input JSON file
    with open(input_file, "r") as file:
        data = json.load(file)

    # Clean the text in each key-value pair of the JSON data
    cleaned_data = {}
    for key, value in data.items():
        cleaned_value = clean_text(value)
        cleaned_data[key] = cleaned_value

    # Save the cleaned data to the output JSON file
    with open(output_file, "w") as file:
        json.dump(cleaned_data, file, indent=4)

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

def generate_srt_from_audio_by_time_interval(audio_file_path):
    def format_timedelta(milliseconds):
        delta = timedelta(milliseconds=milliseconds)
        seconds = delta.total_seconds()
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        milliseconds = delta.total_seconds() * 1000 % 1000
        return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f},{milliseconds:03.0f}"
    
    # Load the audio file
    audio = AudioSegment.from_file(audio_file_path, format="mp3")

    # Split the audio into smaller chunks
    chunk_length_ms = 10000  # Split audio into 10-second chunks
    chunks = make_chunks(audio, chunk_length_ms)

    # Initialize the speech recognizer
    recognizer = sr.Recognizer()

    # Create the SRT file path dynamically
    audio_file_name = os.path.basename(audio_file_path)
    srt_file_name = os.path.splitext(audio_file_name)[0] + ".srt"
    srt_file_path = os.path.join(os.path.dirname(audio_file_path), srt_file_name)

    # Create an SRT file
    with open(srt_file_path, 'w') as srt_file:
        for i, chunk in enumerate(chunks):
            start_time = i * chunk_length_ms
            end_time = (i + 1) * chunk_length_ms

            # Save the chunk as a temporary WAV file
            chunk.export("temp.wav", format="wav")

            # Recognize speech from the temporary WAV file
            with sr.AudioFile("temp.wav") as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)

            # Write the subtitle to the SRT file
            subtitle = f"{i+1}\n{format_timedelta(start_time)} --> {format_timedelta(end_time)}\n{text}\n\n"
            srt_file.write(subtitle)

    return srt_file_path

def generate_srt_from_audio(audio_file_path):
    def format_timedelta(seconds):
        delta = timedelta(seconds=seconds)
        hours = delta.seconds // 3600
        minutes = (delta.seconds // 60) % 60
        seconds = delta.seconds % 60
        milliseconds = delta.microseconds // 1000
        return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f},{milliseconds:03.0f}"


    # Get location of ffmpeg that is required 
    AudioSegment.converter = os.getcwd()+ "\\ffmpeg.exe"                    
    AudioSegment.ffprobe   = os.getcwd()+ "\\ffprobe.exe"
    
    # Load the audio file
    # audio = AudioSegment.from_file(audio_file_path, format="mp3", ffmpeg = "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe")
    audio = AudioSegment.from_file(audio_file_path)

    chunks = split_on_silence(audio,min_silence_len=1000,silence_thresh=-24, keep_silence=True)

    # Initialize the speech recognizer
    recognizer = sr.Recognizer()

    # Create the SRT file path dynamically
    audio_file_name = os.path.basename(audio_file_path)
    srt_file_name = os.path.splitext(audio_file_name)[0] + ".srt"
    srt_file_path = os.path.join(os.path.dirname(audio_file_path), srt_file_name)
    
    # minimum chunk length
    target_length = 5 * 1000 # 5 seconds
    output_chunks = [chunks[0]]
    for chunk in chunks[1:]:
        if len(output_chunks[-1]) < target_length:
            output_chunks[-1] += chunk
        else:
            # if the last output chunk
            # is longer than the target length,
            # we can start a new one
            output_chunks.append(chunk)
            
    # Create an SRT file
    time = 0
    with open(srt_file_path, 'w') as srt_file:
        for i, chunk in enumerate(output_chunks):
            start_time = time
            end_time = time + chunk.duration_seconds
            time += chunk.duration_seconds
            print(time)

            # Save the chunk as a temporary WAV file
            chunk.export("temp.wav", format="wav")

            # Recognize speech from the temporary WAV file
            with sr.AudioFile("temp.wav") as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)

            # Write the subtitle to the SRT file
            subtitle = f"{i+1}\n{format_timedelta(start_time)} --> {format_timedelta(end_time)}\n{text}\n\n"
            srt_file.write(subtitle)

    return srt_file_path

def createClip(post, mp3_file="post-text.mp3"):

    def get_video_file():
        background_video_dir = os.path.join(os.getcwd(), "resources", "background_videos")
        background_video_files  = [f for f in os.listdir(background_video_dir) if f.endswith(".mp4")]
        background_video_file = os.path.join(background_video_dir, random.choice(background_video_files))
        return background_video_file
    
    def get_screenshot_file(post):
        screenshots = get_full_screenshot(post['url'], max_num_of_comments=3)
        # screenshots = []
        # screenshots_dir = os.path.join(os.getcwd(), "resources", "screenshots")
        # # screenshots = [f for f in os.listdir(screenshots_dir) if f.endswith(".png")]
        # screenshots.append(os.path.join(screenshots_dir, "screenshot_title.png"))
        # screenshots.append(os.path.join(screenshots_dir, "screenshot_body.png"))
        # screenshots.append([os.path.join(screenshots_dir, f) for f in os.listdir(screenshots_dir) if "comment" in f])
        return screenshots

    def create_post_text_for_video(post, audio_duration, post_meta, meta_duration):
        total_words = len(post.split())
        wps_from_audio = total_words / audio_duration

        # Split the text into a list of paragraphs
        paragraph_list = post.split("\n\n")
        text_clips = []

        # Add meta textclip
        meta_clip = TextClip(post_meta, font=font, fontsize=fontsize+14, color=color, bg_color=bg_color, align='West', method='caption', size=(mobile_text_size[0],None))
        meta_clip = meta_clip.set_duration(meta_duration).set_position('center') # 5 second opener!
        text_clips.append(meta_clip) # intro text

        time = meta_duration + audio_duration
        # for i, paragraph in enumerate(paragraph_list):
        #     if paragraph: 
        #         num_words = len(paragraph.split())
        #         duration = (num_words / wps_from_audio)
        #         text_clip = TextClip(paragraph, font=font, fontsize=fontsize, color=color, bg_color=bg_color, align='West', method='caption', size=(mobile_text_size[0],None))
        #         text_clip = text_clip.set_start(time).set_position('center').set_duration(duration).set_opacity(opacity)
        #         text_clips.append(text_clip)
        #         time += duration

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
    post_meta = format_meta_text(post)
    screenshot_files = get_screenshot_file(post)
    background_video_file = get_video_file()
    mp4_file = "Top AITA of the Day.mp4"
    width = 720
    height = int(width*9/16) # 16/9 screen
    video_size = width,height
    mobile_video_size = height,width
    text_size = (int(video_size[0]), int(video_size[1]*0.9)) # 16:9
    mobile_text_size = (int(video_size[1]*0.9), int(video_size[0]*0.9)) # 9:16
    font='Arial'
    fontsize=18
    color='white'
    bg_color='black'
    opacity = 0.75
    audio_file = mp3_file
    meta_duration = 5
    TextClip.list('color')
    # Set up the audio clip from our post to TTS
    audio = AudioFileClip(text_to_speech_pyttsx3(post_full, audio_file))
    audio = audio.set_start(meta_duration)
    print("Audio Set...")

    srt_file = generate_srt_from_audio(audio_file)
    generator = lambda txt: TextClip(txt, font=font, fontsize=fontsize, color=color, bg_color=bg_color, align='West', method='caption', size=(mobile_text_size[0],None))
    # subs = [((0, 2), 'subs1'),
    #         ((2, 4), 'subs2'),
    #         ((4, 6), 'subs3'),
    #         ((6, 10), 'subs4')]

    subtitles = SubtitlesClip(srt_file, generator)
    subtitles = subtitles.set_position(("center",0.75), relative=True).set_start(meta_duration).set_duration(audio.duration)
    # Set up the video clip from our screenshot or videos
    
    # Intro Clip
    # intro_video = ImageClip(screenshot_files[0], duration=meta_duration)
    # intro_video = intro_video.resize((mobile_text_size[0], 50)).set_position("center")
    
    main_post_video = ImageClip(screenshot_files[0], duration=audio.duration)
    main_post_video = main_post_video.resize((mobile_text_size[0], 50)).set_position(("center", 0.1), relative=True).set_start(meta_duration).set_duration(audio.duration)

    # video = ImageSequenceClip(screenshot_file, fps=1)
    video = VideoFileClip(background_video_file).loop(duration=10)
    video = video.set_start(meta_duration).set_duration(audio.duration)
    video = video.resize(mobile_video_size)
    background_clip = video.set_audio(audio)
    print("Background Video Set...")

    # Set up the text clip overlays for the video
    text_clips = create_post_text_for_video(post_full, audio.duration, post_meta, meta_duration)
    # text_clips = create_post_text_for_video_scroll(post_full, audio.duration)
    print("Texts Generating...")

    # Bind the audio/video to the textclips
    final_clip = CompositeVideoClip([background_clip, main_post_video, *text_clips, subtitles], size=mobile_video_size)
    # final_clip = CompositeVideoClip([background_clip, *text_clips], size=mobile_video_size)
    final_clip.write_videofile(mp4_file)

    return mp4_file

# def upload_to_youtube(mp4_file, meta_data_file):

#     uploader = YouTubeUploader(mp4_file, meta_data_file)
#     was_video_uploaded, video_id = uploader.upload()
#     assert was_video_uploaded
#     return

def move_video(mp4_file):
    # Set the source and destination paths
    mp4_source = os.path.join(os.getcwd(), mp4_file)
    mp4_dest_folder = os.path.join(os.getcwd(), "resources", "posted_videos")
    
    # Create the destination folder if it doesn't exist
    if not os.path.exists(mp4_dest_folder):
        os.makedirs(mp4_dest_folder)
    
    # Get a list of existing mp4 files in the destination folder
    existing_mp4_files = [f for f in os.listdir(mp4_dest_folder) if f.endswith(".mp4")]
    
    # Determine the next available number for the new filename
    next_num = len(existing_mp4_files) + 1
    
    # Construct the new filename
    new_mp4_file = f"{os.path.splitext(mp4_file)[0]}#{next_num}.mp4"
    mp4_dest = os.path.join(mp4_dest_folder, new_mp4_file)
    
    # Copy the file to the new destination
    with open(mp4_source, 'rb') as fsrc, open(mp4_dest, 'wb') as fdest:
        fdest.write(fsrc.read())
    
    # Remove the old file
    os.remove(mp4_source)

    return mp4_dest

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
    # url = "https://www.reddit.com/r/mildlyinfuriating/top.json?t=day"
    # url = "https://www.reddit.com/subreddits/popular.json"
    post_num = 0  # first (top most post) (usually <25 posts)
    num_of_comments = 3

    # The logic...
    reddit_posts = get_posts(url)
    reddit_post = get_specific_post(reddit_posts, post_num)
    comments = get_comments(reddit_post['url'], num_of_comments)
    combined_post = combine_post_comments(reddit_post, comments)
    mp4_file = createClip(combined_post)
    # meta_data_file = "yt_meta_data.json"
    # upload_to_youtube(mp4file, meta_data_file)
    move_video(mp4_file)

    # Anything extra... 
    # print_post(reddit_posts, post_num)
    # print_comments(comments)
    # print_json(combined_post)

if __name__ == "__main__":
    main()