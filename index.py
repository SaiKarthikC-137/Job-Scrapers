from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time

# Setup Chrome options to prevent detection
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
simplify_url  = "https://simplify.jobs/jobs?experience=Internship%3BEntry%20Level%2FNew%20Grad&category=Software%20Engineering%3BBackend%20Engineering%3BBusiness%20%26%20Strategy"
# Initialize ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
first_flag = True


# Function to login
def login(email, password):
    driver.get("https://simplify.jobs/auth/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
    
    # Enter login details
    email_element = driver.find_element(By.ID, "email")
    email_element.send_keys(email)
    
    password_element = driver.find_element(By.ID, "password")
    password_element.send_keys(password)
    
    # Submit the form
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()
    
    # Wait for user input after entering login details
    input("Please solve the CAPTCHA if present and press Enter to continue...")

    if driver.current_url == "https://simplify.jobs/dashboard":
        print("Login successful")
        driver.get(simplify_url)
        time.sleep(5)

# Function to handle job application process for a single job
def apply_for_job(first_job = False):
    # Wait for the page to load and locate the "Apply" button
    try:
        apply_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Apply')]"))
        )
        # Attempt to click using JavaScript
        driver.execute_script("arguments[0].click();", apply_button)
    except Exception as e:
        print("Failed to click the Apply button:", str(e))
        return
    if first_job:
        # Handle the first-time popup with extended wait times
        try:
            # Wait for the checkbox to appear and be clickable
            checkbox = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "preventShow"))
            )
            checkbox.click()
            print("Checked 'Don't show this popup again'.")

            # Wait for the "Proceed anyway" button to appear and be clickable
            proceed_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Proceed anyway')]"))
            )
            proceed_button.click()
            print("Clicked 'Proceed anyway'.")
        except Exception as e:
            print("First-time popup did not appear or failed to interact with it:", str(e))

    # Wait for the new tab to open
    WebDriverWait(driver, 20).until(lambda d: len(d.window_handles) > 1)
    
    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[1])
    
    # Capture the new URL
    new_url = driver.current_url
    print(f"Redirected to: {new_url}")
    
    # Close the new tab and switch back to the original tab
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # Check for and close the second popup if it appears
    try:
        # Try to click the "Close" button
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close' and @data-testid='close-modal']"))
        )
        close_button.click()
        print("Second popup closed successfully using 'Close' button.")
    except Exception as e:
        print("Failed to close the popup using 'Close' button:", str(e))
        try:
            # Try to click the "No" button if "Close" fails
            no_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='No']"))
            )
            no_button.click()
            print("Second popup closed successfully using 'No' button.")
        except Exception as e:
            print("Failed to close the second popup using both 'Close' and 'No' buttons:", str(e))

# Function to scroll through the page using the Page Down key
def scroll_page_down():
    body = driver.find_element(By.XPATH, "//div[@data-testid='job-card']/ancestor::button")
    for _ in range(30):  # Adjust the range for more or fewer scrolls
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)  # Wait for a moment to allow content to load

# Function to scroll within a specific div that contains job listings
def scroll_within_div():
    # Locate the div that contains the job listings
    scrollable_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'flex h-screen flex-col gap-4 overflow-y-auto p-4')]"))
    )
    for _ in range(5):  # Adjust the range for more or fewer scrolls
        driver.execute_script("arguments[0].scrollTop += arguments[0].offsetHeight;", scrollable_div)
        time.sleep(2)  # Wait for a moment to allow content to load
# Function to scroll dynamically within a specific div until all jobs are loaded
def scroll_until_all_jobs_loaded():
    # Locate the div that contains the job listings
    scrollable_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'flex h-screen flex-col gap-4 overflow-y-auto p-4')]"))  # Replace 'your-div-class' with the actual class or identifier of the scrollable div
    )

    # Initial count of job cards
    job_count = len(driver.find_elements(By.XPATH, "//div[@data-testid='job-card']/ancestor::button"))

    while True:
        # Scroll within the div
        driver.execute_script("arguments[0].scrollTop += arguments[0].offsetHeight;", scrollable_div)
        time.sleep(2)  # Wait for a moment to allow content to load

        # Get new count of job cards after scrolling
        new_job_count = len(driver.find_elements(By.XPATH, "//div[@data-testid='job-card']/ancestor::button"))

        # If no new jobs are loaded, break the loop
        if new_job_count == job_count:
            print("All jobs have been loaded.")
            break
        else:
            job_count = new_job_count
            print(f"Loaded {job_count} jobs so far...")
# Function to iterate through all jobs and apply
def process_all_jobs():
    scroll_until_all_jobs_loaded()
    job_cards = driver.find_elements(By.XPATH, "//div[@data-testid='job-card']/ancestor::button")
    print(f"Found {len(job_cards)} job listings to process.")

    for index, job_card in enumerate(job_cards):
        try:
            # Scroll to the job card to make sure it's visible
            driver.execute_script("arguments[0].scrollIntoView(true);", job_card)
            time.sleep(1)  # Adding a slight delay to ensure visibility

            print(f"Processing job {index + 1} of {len(job_cards)}")

            # Click the job card to open the job details
            job_card.click()
            time.sleep(3)  # Wait for the job details to load

            # Apply for the job
            if index == 0:
                apply_for_job(first_job=True)  # Handle the first job differently
            else:
                apply_for_job()

        except Exception as e:
            print(f"Error processing job {index + 1}: {e}")
            time.sleep(2)  # Adding a delay to ensure the page loads properly

# Main execution
try:
    # Replace these with your actual login credentials
    email = "ksaikarthik12@gmail.com"
    password = "Mobile12345="
    
    login(email, password)
    process_all_jobs()
finally:
    driver.quit()

