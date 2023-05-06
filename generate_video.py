from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import requests
import time
from dotenv import load_dotenv
import os
import shutil

def download_video_from_search_from_pixabay(search_term, video_index):
    
    # Set up Selenium webdriver
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    # Go to Pixabay Videos homepage
    driver.get("https://pixabay.com/videos/")
    
    time.sleep(2)

    # Find and fill the search input
    search_input = driver.find_element(By.NAME, "q")
    # search_input = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[3]/div[1]/div/form/input")
    # search_input = driver.find_element_by_name("q")
    search_input.send_keys(search_term)
    search_input.submit()
    
    # Wait for search results to load
    time.sleep(2)
    
    # Find the nth video result and click to open it
    video_results = driver.find_elements(By.CLASS_NAME, "item")
    video_result = video_results[video_index - 1]
    video_result.click()
    
    # Wait for the video player to load
    time.sleep(5)
    
    # Find and click the download button
    # download_button = driver.find_element(By.CLASS_NAME, "download_menu large_menu")
    download_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[2]/div[4]")
    download_button.click()

    time.sleep(5)
    
    # Find the 1080p option
    quality_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[2]/div[4]/div/table/tbody/tr[3]/td[1]/input") # 720p
    quality_button.click()

    time.sleep(5)

    # Click download button
    final_download_button  = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[2]/div[4]/div/a[2]")
    final_download_button.click()

    # Wait for the download to finish
    time.sleep(30)
    
    # Close the browser window
    driver.quit()

def download_coverr_video(search_query, item_num=0, save_path="C:\\Users\\longp\\Downloads"):
    # Load Chrome driver and navigate to Coverr
    driver = webdriver.Chrome()
    driver.get(f"https://coverr.co/s?q={search_query}")

    time.sleep(3)

    # Wait for search input to be loaded and enter search query
    # search_input = WebDriverWait(driver, 60).until(
    #     EC.presence_of_element_located((By.CLASS_NAME, "video-link"))
    # )
    search_input = driver.find_elements(By.CLASS_NAME, "video-link")
    search_input[item_num].click()

    # Wait for search results to load and click on the first video
    # video = WebDriverWait(driver, 60).until(
    #     EC.presence_of_element_located((By.CLASS_NAME, "acu-video-player__video"))
    # )

    # Wait for download button to be loaded and click it
    download_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "download-split-button__text"))
    )
    download_button.click()

    time.sleep(2)

    def move_file_from_downloads_to_working_dir(search_query, save_path):

      # Move downloaded mp4 to working dir
      downloads_folder = save_path
      latest_time = 0
      latest_file_name = ""
      for f in os.listdir(downloads_folder):
        if f.endswith('.mp4'):
            file_path = os.path.join(downloads_folder, f)
            # print(file_path)
            if os.path.getctime(file_path) > latest_time:
                latest_time = os.path.getctime(file_path)
                latest_file = file_path
                latest_file_name = f
      source_path = latest_file
      destination_path = f"C:\\Users\\longp\\Documents\\Coding\\AITA_Visualizer\\aita_visualizer\\background_videos\\{search_query}.mp4"
      shutil.move(source_path, destination_path)  # Move the file to the destination path
      return

    move_file_from_downloads_to_working_dir(search_query, save_path)
    time.sleep(2)
    
    # Close the driver and return the file path
    driver.quit()
    return

def download_hugging_face_gif(search_query):

    # Load Chrome driver and navigate to Coverr
    driver = webdriver.Chrome()
    driver.get(f"https://huggingface.co/spaces/damo-vilab/modelscope-text-to-video-synthesis")

    time.sleep(2)
  
    # Wait for search input to be loaded and enter search query
    # search_input = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '/html/body/gradio-app/div/div/div/div/div/div[2]/div[1]/div/div/div/label/input')))
    # search_input = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prompt-text-input"]/label/input')))
    search_input = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.scroll-hide.svelte-4xt1ch')))
    search_input.send_keys(search_query)
    search_input.send_keys(Keys.RETURN)
    print(search_input)
    time.sleep(20)
    return

def main(): 
  # prompt = "baby"
  prompt = "An astronaut riding a horse"
  item_num = 9
  # download_hugging_face_gif(prompt) # doesn't work...
  # download_coverr_video(prompt, item_num)
  # download_video_from_search_from_pixabay(prompt, item_num)

if __name__ == "__main__":
   main()