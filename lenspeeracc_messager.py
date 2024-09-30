import time
import logging
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(filename='lenspeer_automation_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Function to set up Chrome options and connect to a specific WebSocket Debugger URL
def get_existing_chrome_with_debugger_url(debugger_url):
    chrome_options = Options()
    # Connect to the WebSocket Debugger URL for a specific tab
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Navigate to the specific tab using the WebSocket Debugger URL
    driver.execute_cdp_cmd("Target.attachToTarget", {"targetId": debugger_url})

    return driver


# Function to load cookies from a JSON file
def load_cookies(driver, cookies_file):
    try:
        driver.get("https://lenspeer.com")  # Load any page before adding cookies
        with open(cookies_file, 'r') as file:
            cookies = json.load(file)["cookies"]
            for cookie in cookies:
                if 'expiry' in cookie:
                    cookie['expiry'] = int(cookie['expiry'])  # Ensure expiry is an integer
                driver.add_cookie(cookie)
        logging.info("Cookies loaded successfully.")
        driver.refresh()  # Refresh to apply cookies
    except Exception as e:
        logging.error(f"Error loading cookies: {str(e)}")


# Automate sending messages to "Who to Follow" profiles
def send_message_to_who_to_follow(driver, message):
    try:
        driver.get("https://lenspeer.com/discover/who-to-follow")
        logging.info("Navigated to the 'Who to Follow' page.")

        profiles = driver.find_elements_by_xpath("//a[contains(@href, '/profile/')]")
        logging.info(f"Found {len(profiles)} profiles.")

        for profile in profiles:
            profile_url = profile.get_attribute('href')
            driver.get(profile_url)
            logging.info(f"Navigated to profile: {profile_url}")

            message_icon = driver.find_element_by_xpath("//button[contains(@aria-label, 'Message')]")
            message_icon.click()
            logging.info("Opened chatbox.")

            chatbox = driver.find_element_by_xpath("//textarea[@id='message']")
            chatbox.send_keys(message)
            logging.info(f"Typed message: {message}")

            send_button = driver.find_element_by_xpath("//button[contains(text(), 'Send')]")
            send_button.click()
            logging.info(f"Sent message to profile: {profile_url}")

            driver.get("https://lenspeer.com/discover/who-to-follow")  # Return to the Who to Follow page

    except Exception as e:
        logging.error(f"Error in messaging process: {str(e)}")


# Main automation process
def main():
    # WebSocketDebuggerUrl from your JSON
    websocket_url = "F19827ABF3ECA6B97C86F76A9BBEF39D"  # Replace with the relevant WebSocket Debugger URL

    driver = get_existing_chrome_with_debugger_url(websocket_url)
    message_content = "Hello! Check out Web3Names.AI, an exciting project in Web3 space!"

    try:
        # Load cookies to maintain session
        load_cookies(driver, "session_cookies.json")

        # Send messages to "Who to Follow" profiles
        send_message_to_who_to_follow(driver, message_content)

    finally:
        input("Press Enter to close the browser...")
        driver.quit()
        logging.info("Automation completed and browser closed.")


if __name__ == "__main__":
    main()
