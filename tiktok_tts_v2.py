import requests
import json
import base64
import re
import os
from tqdm import tqdm
import time

# en_us_001 ∙ Female
# en_us_006 ∙ Male 1
# en_us_007 ∙ Male 2
# en_us_009 ∙ Male 3
# en_us_010 ∙ Male 4

def texttotiktoktts(text="", voice="en_us_001", path="", file_name="tts_audio.mp3"):
    # if i call this too fast, it fails. 
    while(True):    
        try:
            response = requests.post('https://tiktok-tts.weilnet.workers.dev/api/generation',
                                    json={"text": text, "voice": voice})
            jsondata = json.loads(response.text)
            error = jsondata.get("error")

            if error is None:
                audio_base64 = jsondata["data"]
                text = re.sub(r"[^a-zA-Z0-9]+", "", text)[:61]  # Filter and limit export name

                audio_data = base64.b64decode(audio_base64)

                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)

                file_path = os.path.join(path, f"{file_name}.mp3")
                
                # simple with no tqdm 
                # with open(file_path, "wb") as file:
                    # file.write(audio_data)
                
                # with tqdm
                with open(file_path, "wb") as file:
                    total_size = len(audio_data)
                    chunk_size = 4096

                    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Writing audio") as progress_bar:
                        bytes_written = 0

                        while bytes_written < total_size:
                            chunk = audio_data[bytes_written:bytes_written + chunk_size]
                            file.write(chunk)
                            bytes_written += len(chunk)
                            progress_bar.update(len(chunk))

                return True, file_path
            else:
                print(f"Error: {error}")
                return False, error
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            time.sleep(1)
            # return False, "An error has occurred"
