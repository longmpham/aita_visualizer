import os
import shutil
from pydub import AudioSegment
from moviepy.editor import *
from TTS.api import TTS
from pydub import AudioSegment
from shutil import which

coqui_speaker_list = [
    "tts_models/en/jenny/jenny", # OK 
    "tts_models/en/ljspeech/tacotron2-DDC_ph", # OK
    "tts_models/en/ljspeech/fast_pitch", #OK
    "tts_models/en/ljspeech/glow-tts", #WORKS 4
    "tts_models/en/ljspeech/tacotron2-DCA", #BAD 3
    "tts_models/en/multi-dataset/tortoise-v2", #OK but long time and different results
    "tts_models/en/ljspeech/speedy-speech", # 6 error kernel size blah blah
    "tts_models/en/ljspeech/tacotron2-DDC", # BUGS OUT SOMETIMES
    "tts_models/en/ljspeech/vits--neon", # 8 #needs Espeakng
    "tts_models/en/ljspeech/vits", # needs espeakng
    "tts_models/en/vctk/vits", # needs espeakng
    "vocoder_models/en/ljspeech/hifigan_v2", # 11
    "vocoder_models/en/ljspeech/multiband-melgan",
    "vocoder_models/en/ljspeech/univnet",
    "vocoder_models/universal/libri-tts/fullband-melgan",
]


# Text prompts comes in as a list of strings
def generate_TTS_using_coqui(text_prompts):
    def delete_temp_audio(folder_path="resources\\temp\\audio"):
        # If temp folder is found, delete it
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        # Create the folder
        os.mkdir(folder_path)
        
        return
    
    # Print models available for free use
    # for model in TTS.list_models():
    #     print(model)
    # exit()
    # In terminal type below to get list of speaker names.
    # tts --list_models

    # Clear old audio files
    delete_temp_audio()

    # Init TTS
    tts = TTS(model_name=coqui_speaker_list[1], progress_bar=True, gpu=False)
    # Run TTS
    # ❗ Since this model is multi-speaker and multi-lingual, we must set the target speaker and the language
    # Text to speech with a numpy output
    # wav = tts.tts("This is a test! This is also a test!!", speaker=tts.speakers[0], language=tts.languages[0])
    # Text to speech to a file
    tts_files = []
    for i, text in enumerate(text_prompts):
        file_name = f"resources\\temp\\audio\\output_{i+1}.wav"
        tts.tts_to_file(text=text, file_path=file_name, speed=2.0)
        tts_files.append(file_name)

    # Combine audio files
    combined_audio = AudioSegment.empty()
    silent_audio = AudioSegment.silent(0.5*1000)
    for file_name in tts_files:
        audio_segment = AudioSegment.from_wav(file_name)
        combined_audio += audio_segment + silent_audio

    # Speed audio up
    combined_audio = combined_audio.speedup(playback_speed=1.2)

    # Export combined audio to file
    output_file = "resources\\temp\\audio\\post_text.wav"
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