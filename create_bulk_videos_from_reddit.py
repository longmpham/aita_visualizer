import os
import numpy as np
import requests
import time
import json
import pyttsx3
import re
import random
import shutil
import datetime
from datetime import timedelta
from datetime import datetime as dt
from moviepy.editor import *
from gtts import gTTS
import unicodedata
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks
from pydub.silence import split_on_silence
from moviepy.video.tools.subtitles import SubtitlesClip
from get_screenshot import get_full_screenshot
from tts import generate_TTS_using_coqui
from faster_whisper import WhisperModel
from pathlib import Path
from better_profanity import profanity
from tqdm import tqdm
from pydub.playback import play
from tiktok_tts_v2 import texttotiktoktts


def delete_temp(folder_path="resources\\temp"):
    # If temp folder is found, delete it
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    # Create the folder
    os.mkdir(folder_path)
    os.mkdir(folder_path + "\\audio")
    
    return

def censor_keywords(text):
    censored_text = profanity.censor(text)
    return censored_text

def utc_to_relative_time(utc_timestamp):
    
    now = dt.utcnow()
    post_time = dt.utcfromtimestamp(utc_timestamp)
    # now = datetime.datetime.now()
    # post_time = datetime.datetime.fromtimestamp(utc_timestamp)
    
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

    # # update comments_ups to 0 if none is found for sorting
    # for comment in comments_data:
    #     if "ups" in comment["data"] and not comment["data"]["ups"]:
    #         comment["data"]["ups"] = 1

    # Sort comments_data by largest "ups"
    # comments_data.sort(key=lambda comment: comment["data"].get("ups",1), reverse=True)
    
    # Print the sorted comments
    # for i, comment in enumerate(comments_data):
    #     ups = comment["data"].get("ups",1)
    #     print(f"{i} - Ups: {ups}")
    # exit()
    
    # get the post body data from data
    comments = []
    for index, comment in enumerate(comments_data):
        # Skip comment if more than 30 words
        comment_body = comment["data"]["body"]
        word_count = len(comment_body.split())
        if word_count > 30:
            continue
        if comment_body == "[removed]" or comment_body == "[deleted]":
            continue
        ups = comment["data"].get("ups",1)
        # print(f"{index} - Ups: {ups}")
        comments.append({
            "index": str(index+1),
            "author": comment["data"]["author"],
            "comment": comment["data"]["body"],
            # "comment": censor_keywords(comment_body),
            "ups": str(comment["data"]["ups"]),
            "utc_timestamp": comment["data"]["created_utc"],
            "relative_time": utc_to_relative_time(comment["data"]["created_utc"]),
            "date_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment["data"]["created_utc"]))            
        })
        # Check if three comments have been appended
        if len(comments) == max_num_of_comments:
            break
    
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
        # if NSFW, go next
        # print(post["data"]["over_18"])
        if post["data"]["over_18"] == True: 
            continue
        
        title = post["data"]["title"]
        selftext = post["data"]["selftext"]
        author = post["data"]["author"]
        ups = str(post["data"]["ups"])
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

def combine_post_comments(post, comments, post_index):
    # what is the type of post and comments?
    # print(type(post)) # dict
    # print(type(comments)) # list of dict
    merged_post = post
    merged_post["comments"] = comments
    file_name = f"resources\\temp\\post_{post_index}.json"
    save_json(merged_post, file_name)
    clean_json_file(file_name, file_name)
    json_data = load_json_file(file_name)
    # print(json_data)
    return json_data
    # return merged_post

def save_json(post, file_name):
    with open(file_name, "w") as outfile:
        # Write the JSON data to the file with indentation for readability
        json.dump(post, outfile, indent=4)

def print_json(json_object):
    print(json.dumps(json_object, indent=2))

def text_to_speech_pyttsx3(post, output_file="resources\\temp\\audio\\post_text.wav"):
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

def text_to_speech_gtts(sentences):
    def delete_temp_audio(folder_path="resources\\temp\\audio"):
        # If temp folder is found, delete it
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        # Create the folder
        os.mkdir(folder_path)
        
        return
    
    delete_temp_audio()
    
    # Combine audio files
    silence_time = 1.5 # seconds
    sample_rate = 16000
    change_speed = True
    audio_speed = 1.25
    change_pitch = True
    octaves = 0.25 # For decreasing, octave can be -0.5, -2 etc.

    # Initialize an empty AudioSegment object with the desired sample rate
    combined_audio = AudioSegment.silent(duration=silence_time*100, frame_rate=sample_rate)

    # generate the audio and combine them with a short silence after each sentence
    for i, sentence in tqdm(enumerate(sentences), desc="Generating Speech", total=len(sentences)):
        output_file = f"resources\\temp\\audio\\post_text_{i}.wav"
        tts = gTTS(sentence, lang='en')
        tts.save(output_file)
        audio_segment = AudioSegment.from_file(output_file)
        combined_audio += audio_segment.set_frame_rate(sample_rate)  # Set the frame rate to the desired sample rate

    # Speed audio up
    if(change_speed):
        combined_audio = combined_audio.speedup(playback_speed=audio_speed)
    
    # pitch
    if(change_pitch):
        new_sample_rate = int(combined_audio.frame_rate * (2.0 ** octaves))
        combined_audio = combined_audio._spawn(combined_audio.raw_data, overrides={'frame_rate': new_sample_rate})
    
    # Export combined audio to file
    output_file = "resources\\temp\\audio\\post_text.wav"
    combined_audio.export(output_file, format="wav")
    return output_file

def generate_TTS_using_TikTok(sentences):
    def delete_temp_audio(folder_path="resources\\temp\\audio"):
        # If temp folder is found, delete it
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        # Create the folder
        os.mkdir(folder_path)
        
        return
    
    delete_temp_audio()
    
    path = os.getcwd() + "\\resources\\temp\\audio"
    tts_files = []
    success = False
    # Initialize an empty AudioSegment object with the desired sample rate
    sample_rate = 16000
    silence_time = 1
    change_speed = True
    audio_speed = 1.1
    change_pitch = False
    octaves = 0.25 # For decreasing, octave can be -0.5, -2 etc.
    combined_audio = AudioSegment.silent(duration=silence_time*100, frame_rate=sample_rate)  
    for i, sentence in enumerate(sentences):
        
        success, tts_file = texttotiktoktts(sentence, "en_us_001", path, file_name=f"audio_tts_{i}")
        if not success: exit()
        print(f"generated tts_file at: {tts_file}")
        tts_files.append(tts_file)
        # print(tts_file)
        audio_segment = AudioSegment.from_file(tts_file)
        combined_audio += audio_segment.set_frame_rate(sample_rate)  # Set the frame rate to the desired sample rate
    
    
    # Speed audio up
    if(change_speed):
        combined_audio = combined_audio.speedup(playback_speed=audio_speed)
    
    # pitch
    if(change_pitch):
        new_sample_rate = int(combined_audio.frame_rate * (2.0 ** octaves))
        combined_audio = combined_audio._spawn(combined_audio.raw_data, overrides={'frame_rate': new_sample_rate})
    # Export combined audio to file
    output_file = "resources\\temp\\audio\\post_text.wav"
    combined_audio.export(output_file, format="wav")
    return output_file

def clean_json_file(input_file, output_file):
    def clean_text(text):
        # Convert to string if input is not already a string
        if not isinstance(text, str):
            text = str(text)

        # Remove Unicode characters
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

        # Remove newlines ("\n")
        text = re.sub(r"\n+", " ", text)
        
        # Remove Unicode characters
        # text = re.sub(r"\\u\d{4}", "", text)
        
        # Remove other escape characters
        text = re.sub(r"\\[^\w\s]", "", text)
        
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        
        return text.strip()
    
    def clean_dictionary_values(dictionary):
        cleaned_dictionary = {}
        for key, value in dictionary.items():
            if isinstance(value, str):
                cleaned_value = re.sub(r'\\[nrt]', '', value)  # Remove escape characters (\n, \r, \t)
                cleaned_value = re.sub(r'\s+', ' ', cleaned_value)  # Remove extra white spaces
                cleaned_value = cleaned_value.strip()  # Remove leading/trailing white spaces
                cleaned_dictionary[key] = cleaned_value
            else:
                cleaned_dictionary[key] = value
        return cleaned_dictionary

    data = load_json_file(input_file)
    cleaned_data = clean_dictionary_values(data)
    save_json(cleaned_data, output_file)

def load_json_file(file_path):
    data = {}
    with open(file_path) as file:
        data = json.load(file)
    # print(data)
    return data

def format_text(post):
    post_author = post["author"]
    post_title = post["title"]
    post_body = post["selftext"]
    comments = post["comments"] # list of dict
    # print(type(post))
    # print(type(comments))
    post_formatted = [f"{post_author} wrote",f"{post_title}", post_body]
    # post_formatted = post_title + post_body
    for comment in comments:
        # print(comment["comment"])
        post_formatted.append(f"{comment['author']} wrote")
        post_formatted.append(f"{comment['comment']}")
        # post_formatted += "\n\n" + comment["comment"]
        # post_formatted += "\n\n" + comment["author"] + " wrote:\n" + comment["comment"]
    # post_formatted += "\n\n" + "Sub, Comment, Like for more!"
    
    post_formatted.append("Sub, Comment, Like for more!")
    # remove any empty elements
    post_formatted = [item for item in post_formatted if item != ""]
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
    chunk_length_ms = 2 *1000  # Split audio into 10-second chunks
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
            chunk.export("resources\\temp\\temp.wav", format="wav")

            # Recognize speech from the temporary WAV file
            with sr.AudioFile("resources\\temp\\temp.wav") as source:
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
    AudioSegment.converter = os.getcwd()+ "\\resources\\ffmpeg\\ffmpeg.exe"                    
    AudioSegment.ffprobe   = os.getcwd()+ "\\resources\\ffmpeg\\ffprobe.exe"
    
    # Load the audio file
    # audio = AudioSegment.from_file(audio_file_path, format="mp3", ffmpeg = "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe")
    audio = AudioSegment.from_file(audio_file_path)

    chunks = split_on_silence(audio,min_silence_len=200,silence_thresh=-24, keep_silence=True)

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
            # print(time)

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

def generate_srt_from_audio_using_whisper(audio_file_path):  
    def format_timedelta(seconds):
        delta = timedelta(seconds=seconds)
        hours = delta.seconds // 3600
        minutes = (delta.seconds // 60) % 60
        seconds = delta.seconds % 60
        milliseconds = delta.microseconds // 1000
        return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f},{milliseconds:03.0f}"
    
    print("generating srt file using whisper...")
    # use large-v2 model and transcribe the audio file
    model_size = "large-v2"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    # print(audio_file_path)
    segments, info = model.transcribe(audio_file_path, beam_size=5)
    segments = list(segments)
    # segments, _ = model.transcribe(
    #     "audio.mp3",
    #     vad_filter=True,
    #     vad_parameters=dict(min_silence_duration_ms=500), # Vad takes out periods of silence
    # )
    # print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    # Create the SRT file path dynamically
    audio_file_name = os.path.basename(audio_file_path)
    srt_file_name = os.path.splitext(audio_file_name)[0] + ".srt"
    srt_file_path = os.getcwd() + f"\\resources\\temp\\{srt_file_name}"
    
    start_end_times = []
    # open a new srt file and save the output from each segment
    with open(srt_file_path, "w") as srt_file:
        # Write each segment to the SRT file
        for index, segment in enumerate(segments, start=1):
        # for index, segment in tqdm(enumerate(segments, start=1), desc="Writing SRT", total=len(segments)):
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            start_end_times.append((segment.start, segment.end))
            # print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, censor_keywords(segment.text)))
            srt_file.write(f"{index}\n")
            # srt_file.write(f"{segment.start:.2f} --> {segment.end:.2f}\n")
            srt_file.write(f"{format_timedelta(segment.start)} --> {format_timedelta(segment.end)}\n")
            srt_file.write(f"{segment.text}\n\n")
    
    return srt_file_path, start_end_times

def generate_concatenated_video(audio_duration, start_duration, mobile_video_size):
    def get_video_file():
        background_video_dir = os.path.join(os.getcwd(), "resources", "background_videos")
        background_video_files = [f for f in os.listdir(background_video_dir) if f.endswith(".mp4")]
        background_video_file = os.path.join(background_video_dir, random.choice(background_video_files))
        return background_video_file

    video_duration = 0.0
    video_clips = []
    video_clip = VideoFileClip(get_video_file())
    video_duration += video_clip.duration
    video_clips.append(video_clip)
    # print(f"first video dur: {video_clip.duration}")
    while video_duration < audio_duration:
        video_clip = VideoFileClip(get_video_file())
        video_clip = video_clip.resize(mobile_video_size)
        
        if video_clip.duration <= audio_duration - video_duration:
            video_clips.append(video_clip)
            video_duration += video_clip.duration
        else:
            video_clip = video_clip.subclip(0, audio_duration - video_duration)
            video_clips.append(video_clip)
            video_duration = audio_duration
    
    # Concatenate all the video clips together and return it
    concatenated_videos = concatenate_videoclips(video_clips)
    final_video = concatenated_videos.set_start(start_duration).set_duration(audio_duration).resize(mobile_video_size)
    return final_video


    # # Load the first background video clip
    # background_video_file = get_video_file()
    # video = VideoFileClip(background_video_file)

    # # Calculate the number of times the video should be repeated
    # num_repeats = int(audio_duration / video.duration)

    # # Calculate the remaining duration after the repeated videos
    # remaining_duration = audio_duration % video.duration
    # print(f'remaining duration: {remaining_duration}')
    # # Create a list to store the video clips
    # video_clips = []

    # # Repeat the video for the required number of times
    # for _ in range(num_repeats):
    #     video_clips.append(video)

    # # If there is a remaining duration, add the next video
    # if remaining_duration > 0:
    #     print('getting new video...')
    #     next_video_path = get_video_file()  # Get the path of the next video
    #     next_video = VideoFileClip(next_video_path)
    #     video_clips.append(next_video)

    # # Concatenate the video clips
    # concatenated_video = concatenate_videoclips(video_clips)

    # # Set the start time and duration of the concatenated video
    # video = concatenated_video.set_start(start_duration).set_duration(audio_duration)

    # # Resize the video
    # video = video.resize(mobile_video_size)

    # return video

def create_clip(post, index, file_name):

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

    def create_post_text_for_video(post, audio_duration, start_duration):

        ending_clip_time = 3
        
        text_clips = []

        # Add Title textclip
        title = post['title']
        title_clip = TextClip(title, font="Impact", fontsize=fontsize+10, color='black', bg_color='white', align='West', method='caption', size=(mobile_text_size[0],None))
        title_clip = title_clip.set_duration(audio_duration-ending_clip_time).set_position(("center",0.2), relative=True).set_opacity(opacity)
        text_clips.append(title_clip) # intro text

        # Add Ending textclip
        ending_text = "Sub, Comment, Like for More! :)"
        ending_comments_clip = TextClip(ending_text, font="Impact", fontsize=fontsize+10, color=color, bg_color=bg_color, align='West', method='caption', size=(mobile_text_size[0],None))
        ending_comments_clip = ending_comments_clip.set_start(audio_duration-ending_clip_time).set_duration(ending_clip_time).set_pos('center').set_opacity(opacity)
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
    
    # post = format_text_json(post)
    # print(post)
    post_full = format_text(post)
    # post_meta = format_meta_text(post)
    # screenshot_files = get_screenshot_file(post)
    # background_video_file = get_video_file()
    mp3_file = "resources\\temp\\audio\\post_text.wav"
    mp4_file = file_name.replace("_", str(index+1))
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
    start_duration = 0
    
    # Set up the audio clip from our post to TTS
    # audio = AudioFileClip(text_to_speech_gtts(post_full))
    audio = AudioFileClip(generate_TTS_using_TikTok(post_full))
    # audio = AudioFileClip(text_to_speech_pyttsx3(post_full, audio_file))
    # print(post_full)
    # audio = AudioFileClip(generate_TTS_using_coqui(post_full))
    # audio = AudioFileClip(audio_file)
    audio = audio.set_start(start_duration)

    # srt_file = generate_srt_from_audio(audio_file)
    srt_file, start_end_times = generate_srt_from_audio_using_whisper(audio_file)
    generator = lambda txt: TextClip(txt, font=font, fontsize=fontsize, color=color, bg_color=bg_color, align='West', method='caption', size=(mobile_text_size[0],None))
    # subs = [((0, 2), 'subs1'),
    #         ((2, 4), 'subs2'),
    #         ((4, 6), 'subs3'),
    #         ((6, 10), 'subs4')]

    subtitles = SubtitlesClip(srt_file, generator)
    subtitles = subtitles.set_position(("center",0.8), relative=True).set_start(start_duration).set_duration(audio.duration) # bottom of screen
    # subtitles = subtitles.set_position(("center","center"), relative=True).set_start(start_duration).set_duration(audio.duration).set_opacity(opacity) # middle of screen
    print("Subtitles Set...")
    
    background_clip = generate_concatenated_video(audio.duration, start_duration, mobile_video_size)
    background_clip = background_clip.set_audio(audio)
    print("Background Video Set...")
    
    # image_clips = []
    # print(screenshot_files)
    # for file in screenshot_files:
    #     print(file)
    # for a,b in start_end_times:
    #     print(a,b)
    # print(start_end_times)
    # exit()
    # for i, (start, end) in enumerate(start_end_times):
    #     print(f"Index: {i}, Start time: {start}, End time: {end}")
    #     image_clip = ImageClip(screenshot_files[i])
    #     image_clip = image_clip.set_position(("center","center"), relative=True).set_start(start).set_duration(end).set_opacity(1).resize(width=mobile_text_size[0])#resize((720*0.9,(1280*0.9)*9/16))
    #     image_clips.append(image_clip)
    # image_clip = ImageClip(screenshot_files[1])
    # image_clip_comment_1 = ImageClip(screenshot_files[2])
    # image_clip_comment_2 = ImageClip(screenshot_files[3])
    # image_clip_comment_3 = ImageClip(screenshot_files[4])

    # Set up the text clip overlays for the video
    text_clips = create_post_text_for_video(post, audio.duration, start_duration)
    print("Texts Generating...")

    # Bind the audio/video to the textclips
    # final_clip = CompositeVideoClip([background_clip, subtitles], size=mobile_video_size)
    # final_clip = CompositeVideoClip([background_clip, *text_clips, subtitles, *image_clips], size=mobile_video_size)
    final_clip = CompositeVideoClip([background_clip, *text_clips, subtitles], size=mobile_video_size)
    # final_clip.save_frame("frame.png", t=1)
    # exit()
    final_clip.write_videofile(mp4_file, threads=16, codec='h264_nvenc')
    
    # Clean up
    for clip in text_clips:
        clip.close()
    background_clip.close()
    subtitles.close()
    final_clip.close()
    
    return mp4_file

def move_video(mp4_files):
    # Set the source and destination paths
    mp4_dest_folder = os.path.join(os.getcwd(), "resources", "posted_videos")
    
    # Create the destination folder if it doesn't exist
    if not os.path.exists(mp4_dest_folder):
        os.makedirs(mp4_dest_folder)
    
    # Get a list of existing mp4 files in the destination folder
    existing_mp4_files = [f for f in os.listdir(mp4_dest_folder) if f.endswith(".mp4")]
    
    moved_files = []
    
    for mp4_file in mp4_files:
        mp4_source = os.path.join(os.getcwd(), mp4_file)
        
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
        
        moved_files.append(mp4_dest)
        existing_mp4_files.append(new_mp4_file)
    
    return moved_files

def main():
        
    # Variables to choose from...
    # url = "https://www.reddit.com/r/AmItheAsshole/top.json?t=day"
    url = "https://www.reddit.com/r/AskReddit/top.json?t=day"
    # url = "https://www.reddit.com/r/mildlyinfuriating/top.json?t=day"
    # url = "https://www.reddit.com/subreddits/popular.json"
    # post_num = 0  # first (top most post) (usually <25 posts)
    number_of_posts = 1
    num_of_comments = 3

    now = datetime.date.today()
    formatted_date = now.strftime("%b.%d.%Y")
    file_name = f"Top Reddit Questions of {formatted_date} _ #shorts #questions #curious #random #funny #fyp #reddit.mp4"
    
    start_time = time.time()
    
    # Clean start and delete temp folder
    delete_temp()
    
    # Get Reddit posts from url
    reddit_posts = get_posts(url)
    
    # get all posts and their comments
    json_posts = []
    for i, post in enumerate(reddit_posts):
        if i >= number_of_posts:
            break
        # post = get_specific_post(reddit_posts, i)
        post_comment = get_comments(post['url'], num_of_comments)
        combined_post = combine_post_comments(post, post_comment, i)
        json_posts.append(combined_post)
    
    # make videos for all clips.
    mp4_files = []
    for i, post in enumerate(json_posts):
        # Create the clips
        mp4_file = create_clip(post, i, file_name)
        mp4_files.append(mp4_file)

    end_time = time.time()
    print("Time taken:", end_time - start_time)
    # move_video(mp4_files)

if __name__ == "__main__":
    main()