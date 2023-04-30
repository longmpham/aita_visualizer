from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def generate_video(prompt, output_path):
    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox()

    # Navigate to the text-to-video generator website
    driver.get("https://huggingface.co/spaces/NeuralInternet/Text-to-Video_Playground")

    # Find the input box for the prompt and enter the provided text
    input_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "prompt")))
    input_box.send_keys(prompt)
    input_box.send_keys(Keys.RETURN)

    # Wait for the video to finish generating
    WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//video[@controls]")))

    # Find the video element and get its source URL
    video = driver.find_element_by_tag_name("video")
    video_src = video.get_attribute("src")

    # Download the video to the specified output path
    response = requests.get(video_src)
    with open(output_path, "wb") as f:
        f.write(response.content)

    # Close the browser window
    driver.quit()


def main(): 
  generate_video("This is a test prompt", "output.mp4")

if __name__ == "__main__":
   main()