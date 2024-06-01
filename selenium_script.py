import time
import pymongo
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import uuid
import re
from dotenv import load_dotenv
import os

load_dotenv()


username_env = os.getenv('username')
password_env = os.getenv('password')

print("usernmae", username_env)


def get_ip():
    response = requests.get("https://api.ipify.org?format=json")
    return response.json()["ip"]

def fetch_trending_topics():
    # Setup Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    
    # Set up the proxy (example using ProxyMesh)
    proxy = os.getenv('proxymesh')
    options.add_argument(f'--proxy-server={proxy}')
    
    # Initialize the WebDriver
    driver = webdriver.Chrome()
    # Log in to Twitter
    driver.get("https://x.com/login")
    time.sleep(2)  # Wait for the login page to load
    wait = WebDriverWait(driver, 15)

    username = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete=username]'))
    )
    username.send_keys("BarundeepD8375")

    login_button = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[role=button].r-13qz1uu'))
    )
    login_button.click()

    password = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[type=password]'))
    )
    password.send_keys(password_env)

    login_button = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid*=Login_Button]'))
    )
    login_button.click()

    direct_message_link = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid=AppTabBar_DirectMessage_Link]'))
    )
    
    # Wait for login to complete
    time.sleep(5)
    
    # Fetch trending topics
    driver.get("https://x.com/explore/tabs/keyword")
    time.sleep(2)
    
    try:
        trending_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[aria-label='Timeline: Explore']")))
    except TimeoutException:
        print("Trending topics not found")
        driver.quit()
        return
        
    trending_texts = [element.text for element in trending_elements]
   # print("Fetched trending texts:", trending_texts)  # Debug output

    # Extract only the trending topic names that start with #
    trending_topics = []
    for text in trending_texts:
        #print("Processing text:", text)  # Debug output
        hashtags = re.findall(r'#\w+', text)
        #print("Extracted hashtags:", hashtags)  # Debug output
        trending_topics.extend(hashtags)

    # Get current IP address
    ip_address = get_ip()
    
    # Generate unique ID and get current time
    unique_id = str(uuid.uuid4())
    end_time = datetime.now()
    
    # Close the WebDriver
    driver.quit()
    
    return {
        "unique_id": unique_id,
        "trending_topics": trending_topics,
        "end_time": end_time,
        "ip_address": ip_address
    }

def store_in_mongodb(data):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["twitter_trends"]
    collection = db["trends"]
    collection.insert_one(data)

if __name__ == "__main__":
    data = fetch_trending_topics()
    if data:
        store_in_mongodb(data)
