from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
import time

def generate_video(prompt):
    # Launch browser
    driver = webdriver.Chrome()
    
    # Navigate to website
    # driver.get('https://huggingface.co/spaces/damo-vilab/modelscope-text-to-video-synthesis')
    driver.get('https://huggingface.co/spaces/NeuralInternet/Text-to-Video_Playground')
    
    # # Wait for all input elements to be present on the page
    # inputs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))

    # # Print the number of input elements found
    # print(inputs)

    # Find input box and enter prompt
    # input_box = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/gradio-app/div/div/div/div/div/div[2]/div[1]/div/div[1]/label/input')))
    # input_box = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="my-test-id"]')))
    # driver.implicitly_wait(10)
    # input_box = driver.find_element(By.CSS_SELECTOR, '[data-testid="my-test-id"]')
    input_box = driver.find_elements(By.TAG_NAME, 'input')
    print(input_box[0])

    input_box[0].send_keys(prompt)

    time.sleep(5)
    # input_box2.send_keys(prompt)
    
    # Wait for video to load and play
    # WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.XPATH, '/html/body/gradio-app/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div[2]/div[1]/video')))
    
    # Wait for video to finish playing
    # WebDriverWait(driver, 60).until_not(EC.presence_of_element_located((By.XPATH, '/html/body/gradio-app/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div[2]/div[1]/video')))
    
    # Save video
    # save_button = driver.find_element_by_xpath('/html/body/gradio-app/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div[2]/div[2]/div/button[2]')
    # save_button.click()
    
    # Close browser
    driver.quit()


def main(): 
  prompt = "twin brothers eating a cake"
  generate_video(prompt)

if __name__ == "__main__":
   main()