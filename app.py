import os
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException, 
                                      NoSuchElementException, 
                                      WebDriverException,
                                      StaleElementReferenceException)
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gmail_automation.log'),
        logging.StreamHandler()
    ]
)

class GmailAutomation:
    def __init__(self, headless=False):
        self.driver = None
        self.headless = headless
        self.setup_driver()
        
    def setup_driver(self):
        """Initialize the WebDriver with optimal settings"""
        try:
            self.driver = self._init_chrome()
            logging.info("Chrome driver initialized successfully")
        except Exception as e:
            logging.error(f"Driver initialization failed: {e}")
            raise RuntimeError("Failed to initialize Chrome driver")

    def _init_chrome(self):
        """Configure Chrome WebDriver with all necessary fixes"""
        chrome_options = webdriver.ChromeOptions()
        
        # Essential options
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        
        # Anti-detection and performance options
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--window-size=1920,1080')
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            logging.error(f"Chrome initialization failed: {e}")
            raise

    def human_delay(self, min_sec=0.5, max_sec=2.0):
        """Random delay between actions to mimic human behavior"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay

    def wait_for_page_load(self, timeout=30):
        """Wait for page to fully load"""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete')

    def human_type(self, element, text, field_name=""):
        """Type text with human-like speed and verification"""
        try:
            self.clear_field(element)
            for char in text:
                element.send_keys(char)
                self.human_delay(0.1, 0.3)  # Human-like typing speed
            
            # Verify content was entered correctly
            entered_text = element.get_attribute('value') if field_name != "body" else element.text
            if entered_text.strip() != text.strip():
                logging.warning(f"Text mismatch in {field_name}, retrying...")
                self.clear_field(element)
                element.send_keys(text)  # Full retry if verification fails
            return True
        except Exception as e:
            logging.error(f"Error in human_type for {field_name}: {e}")
            return False

    def clear_field(self, element):
        """Clear input field thoroughly"""
        element.send_keys(Keys.CONTROL + 'a')
        element.send_keys(Keys.DELETE)
        self.human_delay(0.2, 0.5)

    def login_to_gmail(self, email, password, max_attempts=3):
        """Robust Gmail login implementation"""
        for attempt in range(1, max_attempts + 1):
            try:
                logging.info(f"Login attempt {attempt}/{max_attempts}")
                
                # Load Gmail with multiple URL options
                urls = [
                    'https://mail.google.com',
                    'https://accounts.google.com/ServiceLogin?service=mail',
                    'https://accounts.google.com/v3/signin/identifier?service=mail'
                ]
                
                for url in urls:
                    try:
                        self.driver.get(url)
                        self.wait_for_page_load()
                        self.human_delay(3, 5)
                        if "google.com/accounts" in self.driver.current_url or "mail.google.com" in self.driver.current_url:
                            break
                    except:
                        continue
                else:
                    raise RuntimeError("Could not load Gmail login page")
                
                # Email entry with multiple selectors
                email_success = False
                for selector in [
                    'input[type="email"]',
                    'input[identifier="Email"]',
                    '#identifierId',
                    'input[name="identifier"]'
                ]:
                    try:
                        email_field = WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                        if self.human_type(email_field, email, "email"):
                            email_success = True
                            break
                    except:
                        continue
                
                if not email_success:
                    raise RuntimeError("Could not enter email address")
                
                # Click next button
                next_buttons = [
                    ('id', 'identifierNext'),
                    ('css', 'button[data-primary-action="true"]'),
                    ('xpath', '//span[text()="Next"]')
                ]
                
                for locator_type, locator in next_buttons:
                    try:
                        if locator_type == 'id':
                            next_btn = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.ID, locator)))
                        elif locator_type == 'css':
                            next_btn = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, locator)))
                        else:
                            next_btn = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, locator)))
                        
                        next_btn.click()
                        self.human_delay(2, 4)
                        break
                    except:
                        continue
                else:
                    raise RuntimeError("Could not click next button")
                
                # Password entry
                password_success = False
                for selector in [
                    'input[type="password"]',
                    'input[name="Passwd"]',
                    '#password input'
                ]:
                    try:
                        password_field = WebDriverWait(self.driver, 15).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                        if self.human_type(password_field, password, "password"):
                            password_success = True
                            break
                    except:
                        continue
                
                if not password_success:
                    raise RuntimeError("Could not enter password")
                
                # Submit login
                submit_buttons = [
                    ('id', 'passwordNext'),
                    ('css', 'button[data-primary-action="true"]'),
                    ('xpath', '//span[text()="Next"]')
                ]
                
                for locator_type, locator in submit_buttons:
                    try:
                        if locator_type == 'id':
                            submit_btn = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.ID, locator)))
                        elif locator_type == 'css':
                            submit_btn = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, locator)))
                        else:
                            submit_btn = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, locator)))
                        
                        submit_btn.click()
                        self.human_delay(5, 8)  # Longer delay for login processing
                        break
                    except:
                        continue
                else:
                    raise RuntimeError("Could not submit login")
                
                # Verify login success
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[text()="Compose"]')))
                logging.info("Login successful")
                return True
                
            except Exception as e:
                logging.error(f"Login attempt {attempt} failed: {e}")
                if attempt == max_attempts:
                    self.driver.save_screenshot('login_failure.png')
                    return False
                
                self.driver.delete_all_cookies()
                self.human_delay(5, 10)

    def compose_and_send_email(self, recipient, subject, body, max_attempts=3):
        """Complete email composition and sending with all reliability measures"""
        for attempt in range(1, max_attempts + 1):
            try:
                logging.info(f"Email sending attempt {attempt}/{max_attempts}")
                
                # Click compose button with human delay
                compose_btn = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[text()="Compose"]')))
                self.human_delay(1, 2)
                compose_btn.click()
                
                # Wait for compose window to fully appear
                compose_dialog = WebDriverWait(self.driver, 15).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"]')))
                self.human_delay(1, 2)
                
                # Fill recipient field with multiple selector options
                recipient_success = False
                for selector in [
                    'input[aria-label="To"]',
                    'input[peoplekit-id="BbVjBd"]',
                    'textarea[name="to"]',
                    'input[type="text"][aria-label="To"]'
                ]:
                    try:
                        to_field = WebDriverWait(compose_dialog, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                        if self.human_type(to_field, recipient, "recipient"):
                            recipient_success = True
                            self.human_delay(1, 2)  # Delay after recipient entry
                            break
                    except:
                        continue
                
                if not recipient_success:
                    raise RuntimeError("Could not fill recipient field")
                
                # Fill subject field
                subject_success = False
                for selector in [
                    'input[name="subjectbox"]',
                    'input[aria-label="Subject"]',
                    'input[placeholder="Subject"]',
                    'input[name="subject"]'
                ]:
                    try:
                        subject_field = WebDriverWait(compose_dialog, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                        if self.human_type(subject_field, subject, "subject"):
                            subject_success = True
                            self.human_delay(1, 2)  # Delay after subject entry
                            break
                    except:
                        continue
                
                if not subject_success:
                    raise RuntimeError("Could not fill subject field")
                
                # Fill body content
                body_success = False
                for selector in [
                    'div[aria-label="Message Body"]',
                    'div[role="textbox"]',
                    'div[g_editable="true"]',
                    'div[aria-label="Message Body"] > div'
                ]:
                    try:
                        body_field = WebDriverWait(compose_dialog, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                        body_field.click()
                        self.human_delay(0.5, 1)
                        body_field.send_keys(body)
                        body_success = True
                        self.human_delay(1, 2)  # Delay after body entry
                        break
                    except:
                        continue
                
                if not body_success:
                    raise RuntimeError("Could not fill body field")
                
                # Send email with multiple selector options
                send_success = False
                for selector in [
                    'div[aria-label*="Send"]',
                    'div[role="button"][aria-label*="Send"]',
                    '//div[text()="Send"]',
                    'div[guidedhelpid="send_button"]'
                ]:
                    try:
                        if selector.startswith('//'):
                            send_btn = WebDriverWait(compose_dialog, 10).until(
                                EC.element_to_be_clickable((By.XPATH, selector)))
                        else:
                            send_btn = WebDriverWait(compose_dialog, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        
                        self.human_delay(1, 2)  # Delay before sending
                        send_btn.click()
                        send_success = True
                        break
                    except:
                        continue
                
                if not send_success:
                    raise RuntimeError("Could not click send button")
                
                # Verify send completion
                WebDriverWait(self.driver, 15).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"]')))
                
                logging.info("Email sent successfully")
                return True
                
            except Exception as e:
                logging.error(f"Email sending attempt {attempt} failed: {e}")
                if attempt == max_attempts:
                    self.driver.save_screenshot('send_email_failure.png')
                    return False
                
                # Try to close the compose window if it's stuck
                try:
                    close_btn = self.driver.find_element(By.CSS_SELECTOR, 'div[aria-label*="Close"]')
                    close_btn.click()
                    self.human_delay(2, 3)
                except:
                    pass
                
                self.human_delay(5, 10)  # Wait before retrying

    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("Browser closed successfully")
            except Exception as e:
                logging.error(f"Error closing browser: {e}")