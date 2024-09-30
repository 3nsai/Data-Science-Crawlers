import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import numpy as np
import os
import pickle
from datetime import datetime

# Configure logging
logging.basicConfig(filename='lenspeer_automation_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ML logging setup
ml_log_file = 'ml_feature_logs.txt'


def log_feature_result(feature_name, success):
    """Log the result of a feature's success or failure for ML training."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp},{feature_name},{int(success)}\n"
    with open(ml_log_file, 'a') as log_file:
        log_file.write(log_entry)
    logging.info(f"Logged result for {feature_name}: {'Success' if success else 'Failure'}")


def predict_feature_failure(feature_name):
    """Predict the likelihood of a feature failing using the trained model."""
    if os.path.exists('failure_prediction_model.pkl'):
        with open('failure_prediction_model.pkl', 'rb') as model_file:
            model = pickle.load(model_file)
    else:
        logging.warning("No model found for failure prediction.")
        return None

    feature_data = np.array([[len(feature_name)]])
    prediction = model.predict(feature_data)
    logging.info(f"Predicted failure for {feature_name}: {prediction[0]}")
    return prediction[0]  # Returns 1 if failure is likely, 0 otherwise


def train_failure_model():
    """Train an ML model to predict feature failures based on past logs."""
    if not os.path.exists(ml_log_file):
        logging.warning("No log file found for training the model.")
        return

    data = []
    labels = []
    with open(ml_log_file, 'r') as log_file:
        for line in log_file.readlines():
            parts = line.strip().split(',')
            if len(parts) != 3:
                continue
            feature_name, success = parts[1], int(parts[2])
            data.append([len(feature_name)])
            labels.append(success)

    X = np.array(data)
    y = np.array(labels)

    model = LogisticRegression()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    logging.info(f"Trained failure prediction model with accuracy: {accuracy:.2f}")

    with open('failure_prediction_model.pkl', 'wb') as model_file:
        pickle.dump(model, model_file)


# WebDriver setup with optimizations for speed
def get_webdriver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


# Function to handle switching to the MetaMask window
def switch_to_metamask_window(driver):
    try:
        main_window = driver.current_window_handle
        WebDriverWait(driver, 10).until(lambda d: len(driver.window_handles) > 1)
        metamask_window = [window for window in driver.window_handles if window != main_window][0]
        driver.switch_to.window(metamask_window)
        logging.info("Switched to MetaMask window.")
        return main_window
    except Exception as e:
        logging.error(f"Error switching to MetaMask window: {str(e)}")
        raise


# Open LensPeer and log in via MetaMask
def login_lenspeer(driver):
    try:
        if predict_feature_failure("login_lenspeer"):
            logging.warning("Predicted failure for login_lenspeer. Proceeding anyway.")

        driver.get("https://lenspeer.com/home")
        logging.info("Navigated to LensPeer home page.")

        sign_in_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="header"]/div[3]/button[2]'))
        )
        sign_in_button.click()
        logging.info("Clicked the Sign In button.")

        connect_wallet_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Connect Wallet')]"))
        )
        connect_wallet_button.click()
        logging.info("Clicked the Connect Wallet button.")

        metamask_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '/html/body/w3m-modal//wui-flex/wui-card/w3m-router//div/w3m-connect-view//wui-flex/wui-list-wallet[2]//button'))
        )
        metamask_button.click()
        logging.info("Clicked the MetaMask wallet connection button.")

        main_window = switch_to_metamask_window(driver)
        time.sleep(5)  # Wait for manual interaction with MetaMask
        driver.switch_to.window(main_window)
        logging.info("Switched back to the main window.")

        log_feature_result("login_lenspeer", True)
    except (NoSuchElementException, TimeoutException, WebDriverException) as e:
        logging.error(f"Error during login: {str(e)}")
        log_feature_result("login_lenspeer", False)
        raise


# Automate visiting profiles and sending messages
def send_message_to_who_to_follow(driver, message):
    try:
        if predict_feature_failure("send_message_to_who_to_follow"):
            logging.warning("Predicted failure for send_message_to_who_to_follow. Proceeding anyway.")

        driver.get("https://lenspeer.com/discover/who-to-follow")
        logging.info("Navigated to the 'Who to Follow' page.")

        profiles = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/profile/')]"))
        )
        logging.info(f"Found {len(profiles)} profiles on the 'Who to Follow' page.")

        for profile in profiles:
            profile_url = profile.get_attribute('href')
            driver.get(profile_url)
            logging.info(f"Navigated to profile: {profile_url}")

            message_icon = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Message')]"))
            )
            message_icon.click()
            logging.info("Clicked the message icon.")

            chatbox = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@id='message']"))
            )
            chatbox.send_keys(message)
            logging.info(f"Entered the message: {message}")

            send_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send')]"))
            )
            send_button.click()
            logging.info(f"Sent the message to profile: {profile_url}")

            log_feature_result("send_message_to_who_to_follow", True)
            driver.get("https://lenspeer.com/discover/who-to-follow")
    except (NoSuchElementException, TimeoutException, WebDriverException) as e:
        logging.error(f"Error while sending message: {str(e)}")
        log_feature_result("send_message_to_who_to_follow", False)
        raise


# Main automation process
def main():
    driver = get_webdriver()
    message_content = "Hello! Have you heard about Web3Names.AI? It's a new and exciting project in the Web3 space!"

    try:
        # Log in to LensPeer via MetaMask
        login_lenspeer(driver)

        # Send messages to profiles on the "Who to Follow" page
        send_message_to_who_to_follow(driver, message_content)

    finally:
        input("Press Enter to close the browser...")
        driver.quit()
        logging.info("Automation completed and browser closed.")


if __name__ == "__main__":
    main()
