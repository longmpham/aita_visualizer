import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
from pydub import AudioSegment
# import numpy as np

from moviepy.editor import *

from TTS.api import TTS
from pydub import AudioSegment

coqui_speaker_list = [
    "tts_models/en/jenny/jenny", # OK
    "tts_models/en/ljspeech/tacotron2-DCA", #BAD
    "tts_models/en/ljspeech/glow-tts", #BAD
    "tts_models/en/ljspeech/tacotron2-DDC", #BAD
    "tts_models/en/ljspeech/fast_pitch", #OK
    "tts_models/en/multi-dataset/tortoise-v2", #OK but long time and different results
    "tts_models/uk/mai/glow-tts", # BAD
    "tts_models/uk/mai/vits", # BAD
    "tts_models/en/blizzard2013/capacitron-t2-c150_v2", # doesnt work
    "tts_models/en/sam/tacotron-DDC", # doesn't work
    "tts_models/en/ljspeech/neural_hmm", # doesn't work
    "tts_models/en/ljspeech/fast_pitch", # OK
    "tts_models/en/ljspeech/overflow", # doesn't work
]


# Text prompts comes in as a list of strings
def generate_TTS_using_coqui(text_prompts):
    # In terminal type below to get list of speaker names.
    # tts --list_models

    # Init TTS
    tts = TTS(model_name=coqui_speaker_list[0], progress_bar=True, gpu=False)
    # Run TTS
    # ❗ Since this model is multi-speaker and multi-lingual, we must set the target speaker and the language
    # Text to speech with a numpy output
    # wav = tts.tts("This is a test! This is also a test!!", speaker=tts.speakers[0], language=tts.languages[0])
    # Text to speech to a file
    tts_files = []
    for i, text in enumerate(text_prompts):
        file_name = f"resources\\audio\\output_{i+1}.wav"
        tts.tts_to_file(text=text, file_path=file_name)
        tts_files.append(file_name)

    # Combine audio files
    combined_audio = AudioSegment.empty()
    for file_name in tts_files:
        audio_segment = AudioSegment.from_wav(file_name)
        combined_audio += audio_segment

    # Export combined audio to file
    output_file = "post-text.wav"
    combined_audio.export(output_file, format="wav")

    return output_file


# text_prompts = [
#     "hello how are you today?",
#     "I'm doing just fine thank you",
#     "hello how are you today?",
#     "I'm doing just fine thank you",
#     "hello how are you today?",
#     "I'm doing just fine thank you",
# ]
# generate_TTS_using_coqui(text_prompts)