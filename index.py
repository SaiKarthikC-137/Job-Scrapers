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
#simplify_url  = "https://simplify.jobs/jobs?experience=Internship%3BEntry%20Level%2FNew%20Grad&category=Software%20Engineering%3BBackend%20Engineering%3BBusiness%20%26%20Strategy"
simplify_url = "https://simplify.jobs/jobs?experience=Internship%3BEntry%20Level%2FNew%20Grad&category=Software%20Engineering%3BBackend%20Engineering%3BBusiness%20%26%20Strategy&education=Master%27s&minSalary=100000"
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
# Function to extract job details
def extract_job_details():
    job_details = {}
    try:
        # Extract company
        company_element = driver.find_element(By.XPATH, "//div[@class='flex items-center gap-2']/p")
        job_details['company'] = company_element.text
        #print(f"Company: {job_details['company']}")

        # Extract location
        location_element = driver.find_element(By.XPATH, "//div[@class='flex items-center gap-2']//p[@class='text-sm font-bold']")
        job_details['location'] = location_element.text
        #print(f"Location: {job_details['location']}")

        # Extract title and posted_at
        title_element = driver.find_element(By.XPATH, "//div[@class='pb-2']/p[@class='text-left text-xl font-bold text-secondary-400']")
        posted_at_element = driver.find_element(By.XPATH, "//div[@class='pb-2']/p[@class='mt-1 text-left text-sm text-gray-500']")
        job_details['title'] = title_element.text
        job_details['posted_at'] = posted_at_element.text.replace("Posted on ", "")
        #print(f"Title: {job_details['title']}")
        #print(f"Posted At: {job_details['posted_at']}")

        # Extract job type
        job_type_element = driver.find_element(By.XPATH, "//p[contains(@class, 'rounded-full bg-primary-50 px-4 py-2 text-sm text-primary-400')]")
        job_details['job_type'] = job_type_element.text
        #print(f"Job Type: {job_details['job_type']}")

        # Extract company logo URL
        company_logo_element = driver.find_element(By.XPATH, "//a[@class='flex size-[72px] shrink-0 items-start focus:outline-none']/img")
        job_details['company_logo'] = company_logo_element.get_attribute("src")
        #print(f"Company Logo URL: {job_details['company_logo']}")

        # Extract company website URL
        company_website_element = driver.find_element(By.XPATH, "//a[contains(@class, 'flex items-center space-x-2') and contains(text(), 'Website')]")
        job_details['company_website'] = company_website_element.get_attribute("href")
        #print(f"Company Website URL: {job_details['company_website']}")

        # Extract company description
        company_description_element = driver.find_element(By.XPATH, "//p[@class='mt-4 text-left text-sm text-secondary-400']")
        job_details['company_description'] = company_description_element.text
        #print(f"Company Description: {job_details['company_description']}")

    except Exception as e:
        print(f"Failed to extract job details: {str(e)}")
    
    return job_details
# Function to handle job application process for a single job
def apply_for_job(first_job = False):
    retries = 3  # Number of retries for clicking the "Apply" button
    apply_button_clicked = False
    # Extract job details before applying
    job_details = extract_job_details()
    # Attempt to click the "Apply" button with retries
    for attempt in range(retries):
        try:
            apply_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Apply')]"))
            )
            print(f"Apply button found. Attempting to click (Attempt {attempt + 1}).")

            # Attempt to click using JavaScript
            driver.execute_script("arguments[0].click();", apply_button)
            print("Apply button clicked using JavaScript.")
            apply_button_clicked = True
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
            try:
                WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                print("New tab opened successfully.")
                break  # Exit the retry loop if new tab opens
            except:
                print("New tab did not open, retrying...")
                continue  # Retry clicking the "Apply" button

        except Exception as e:
            print(f"Failed to click the Apply button on attempt {attempt + 1}: {str(e)}")

    # If unable to open the new tab after retries, skip to next job
    if not apply_button_clicked or len(driver.window_handles) == 1:
        print("Failed to open new tab after 3 attempts. Skipping this job.")
        return

    
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
        print("Failed to close the popup using 'Close' button")
        try:
            # Try to click the "No" button if "Close" fails
            no_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='No']"))
            )
            no_button.click()
            print("Second popup closed successfully using 'No' button.")
        except Exception as e:
            print("Failed to close the second popup using both 'Close' and 'No' buttons")

# Function to scroll and wait until all jobs are loaded
def scroll_until_all_jobs_loaded():
    job_count = 0
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='job-card']/ancestor::button"))
    )
    while True:
        # Get the current number of job cards
        job_cards = driver.find_elements(By.XPATH, "//div[@data-testid='job-card']/ancestor::button")
        new_job_count = len(job_cards)

        # If no new jobs have been loaded, break the loop
        if new_job_count == job_count:
            print("All jobs have been loaded.")
            break

        job_count = new_job_count
        print(f"Loaded {job_count} jobs so far...")

        # Scroll into view of the last job card
        last_job_card = job_cards[-1]
        driver.execute_script("arguments[0].scrollIntoView(true);", last_job_card)
        time.sleep(5)
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

