from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import hashlib
import pandas as pd
from datetime import datetime

# Function to initialize the Chrome driver
def initialize_driver(headless=False):
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")

    if headless:
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

simplify_url = "https://simplify.jobs/jobs?state=United%20States&points=71.5388001%3B-66.885417%3B18.7763%3B-180&country=United%20States&experience=Internship%3BEntry%20Level%2FNew%20Grad%3BJunior%3BMid%20Level&category=Software%20Engineering%3BBackend%20Engineering%3BFull-Stack%20Engineering%3BDevOps%20%26%20Infrastructure%3BSoftware%20Development%20Management%3BFrontend%20Engineering%3BSoftware%20QA%20%26%20Testing%3BDevOps%20Engineering%3BMobile%20Engineering%3BCloud%20Engineering%3BIOS%20Development%3BAndroid%20Development%3BWeb%20Development"
job_category = "Software Engineer"

# Initialize driver in non-headless mode for login
driver = initialize_driver(headless=False)
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

def generate_unique_id(input_string):
    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()

    # Update the hash object with the bytes of the input string
    hash_object.update(input_string.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    unique_id = hash_object.hexdigest()

    return unique_id

# Function to transfer cookies to the headless driver
def transfer_cookies(source_driver, target_driver):
    cookies = source_driver.get_cookies()
    for cookie in cookies:
        target_driver.add_cookie(cookie)

# Switch to headless mode after logging in
def switch_to_headless():
    global driver
    old_driver = driver
    driver = initialize_driver(headless=True)
    driver.get(simplify_url)
    transfer_cookies(old_driver, driver)
    driver.refresh()
    old_driver.quit()
    print("Switched to headless mode.")

# Function to extract job details using BeautifulSoup
def extract_job_details_soup(soup):
    job_details = {}
    try:
        # Extract company
        company_element = soup.find("div", class_="flex items-center gap-2").find("p")
        job_details['company'] = company_element.get_text(strip=True)
        
        # Extract location
        location_element = soup.find("div", class_="flex items-center gap-2").find("p", class_="text-sm font-bold")
        job_details['location'] = location_element.get_text(strip=True)

        # Extract title and posted_at
        title_element = soup.find("p", class_="text-left text-xl font-bold text-secondary-400")
        posted_at_element = soup.find("p", class_="mt-1 text-left text-sm text-gray-500")
        job_details['title'] = title_element.get_text(strip=True)
        job_details['country'] = "United States"
        
        posted_at_text = posted_at_element.get_text(strip=True).replace("Posted on ", "").replace("Updated on ", "")
        job_details['posted_at'] = datetime.now().strftime('%Y-%m-%d') if "Confirmed live in the last 24 hours" in posted_at_text else datetime.strptime(posted_at_text, '%m/%d/%Y').strftime('%Y-%m-%d')

        job_details['job_reference'] = generate_unique_id(job_details['title'] + job_details['company'] + job_details['location'])

        # Extract job type
        job_type_element = soup.find("p", class_="rounded-full bg-primary-50 px-4 py-2 text-sm text-primary-400")
        job_details['job_type'] = job_type_element.get_text(strip=True)

        # Extract company logo URL
        company_logo_element = soup.find("a", class_="flex size-[72px] shrink-0 items-start focus:outline-none").find("img")
        job_details['company_logo'] = company_logo_element['src']

        # Extract company website URL
        company_website_element = soup.find("a", href=True, text="Website")
        job_details['company_website'] = company_website_element['href']

        # Extract company description
        company_description_element = soup.find("p", class_="mt-4 text-left text-sm text-secondary-400")
        job_details['company_description'] = company_description_element.get_text(strip=True)

        # Extract job description (HTML content)
        job_description_element = soup.find("div", class_="prose prose-sm text-left hidden")
        job_details['description'] = str(job_description_element)

        try:
            # Extract compensation details
            compensation_element = soup.find("p", class_="text-base font-bold text-secondary-400")
            compensation_text = compensation_element.get_text(strip=True)

            # Extract min, max compensation
            min_compensation = max_compensation = None
            compensation_pattern = r"\$([\d,\.]+)(k?) - \$([\d,\.]+)(k?)"
            match = re.search(compensation_pattern, compensation_text)
            if match:
                min_comp = match.group(1).replace(',', '')
                max_comp = match.group(3).replace(',', '')
                
                min_compensation = float(min_comp) * (1000 if match.group(2) == 'k' else 1)
                max_compensation = float(max_comp) * (1000 if match.group(4) == 'k' else 1)

                job_details['min_compensation'] = int(min_compensation)
                job_details['max_compensation'] = int(max_compensation)

            # Extract compensation time frame if present
            time_frame_element = compensation_element.find("span")
            job_details['compensation_time_frame'] = time_frame_element.get_text(strip=True) if time_frame_element else "Not specified"

            job_details['compensation_currency'] = 'USD'
        
        except Exception as e:
            print("Compensation N/A")
            
        job_details['remote'] = 1 if "remote" in job_details['location'].lower() else 0
        job_details['category'] = job_category

    except Exception as e:
        print(f"Failed to extract job details using BeautifulSoup: {str(e)}")
    
    return job_details

# Function to handle job application process for a single job
def apply_for_job(first_job=False):
    retries = 3
    apply_button_clicked = False
    job_details = {}

    for attempt in range(retries):
        try:
            apply_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Apply')]"))
            )
            print(f"Apply button found. Attempting to click (Attempt {attempt + 1}).")

            driver.execute_script("arguments[0].click();", apply_button)
            print("Apply button clicked using JavaScript.")
            apply_button_clicked = True

            if first_job:
                try:
                    checkbox = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.ID, "preventShow"))
                    )
                    checkbox.click()
                    print("Checked 'Don't show this popup again'.")

                    proceed_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Proceed anyway')]"))
                    )
                    proceed_button.click()
                    print("Clicked 'Proceed anyway'.")
                except Exception as e:
                    print("First-time popup did not appear or failed to interact with it:", str(e))

            try:
                WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                print("New tab opened successfully.")
                break
            except:
                print("New tab did not open, retrying...")
                continue

        except Exception as e:
            print(f"Failed to click the Apply button on attempt {attempt + 1}: {str(e)}")

    if not apply_button_clicked or len(driver.window_handles) == 1:
        print("Failed to open new tab after 3 attempts. Skipping this job.")
        return

    driver.switch_to.window(driver.window_handles[1])
    new_url = driver.current_url
    print(f"Redirected to: {new_url}")
    job_details['url'] = new_url
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    try:
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close' and @data-testid='close-modal']"))
        )
        close_button.click()
        print("Second popup closed successfully using 'Close' button.")
    except:
        try:
            no_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='No']"))
            )
            no_button.click()
            print("Second popup closed successfully using 'No' button.")
        except Exception as e:
            print("Failed to close the second popup using both 'Close' and 'No' buttons")

    # Parse job details using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'lxml')
    job_details.update(extract_job_details_soup(soup))

    return job_details

# Function to scroll and wait until all jobs are loaded
def scroll_until_all_jobs_loaded():
    job_count = 0
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='job-card']/ancestor::button"))
    )
    while True:
        job_cards = driver.find_elements(By.XPATH, "//div[@data-testid='job-card']/ancestor::button")
        new_job_count = len(job_cards)

        if new_job_count == job_count:
            print("All jobs have been loaded.")
            break

        job_count = new_job_count
        print(f"Loaded {job_count} jobs so far...")

        last_job_card = job_cards[-1]
        driver.execute_script("arguments[0].scrollIntoView(true);", last_job_card)
        time.sleep(5)

# Function to iterate through all jobs and apply
def process_all_jobs():
    columns = [
        'location', 'title', 'country', 'job_type', 'posted_at', 'job_reference', 'company', 
        'company_logo', 'company_website', 'company_description', 'category', 'url', 
        'description', 'min_compensation', 'max_compensation', 'compensation_currency', 
        'compensation_time_frame', 'remote'
    ]
    job_data = []

    job_cards = driver.find_elements(By.XPATH, "//div[@data-testid='job-card']/ancestor::button")
    print(f"Found {len(job_cards)} job listings to process.")

    for index, job_card in enumerate(job_cards):
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", job_card)
            time.sleep(1)

            print(f"Processing job {index + 1} of {len(job_cards)}")
            job_card.click()
            time.sleep(3)

            job_details = apply_for_job(first_job=(index == 0))
            job_data.append(job_details)

        except Exception as e:
            print(f"Error processing job {index + 1}: {e}")
            time.sleep(2)

    job_df = pd.DataFrame(job_data, columns=columns)
    job_df.to_pickle("job_data.pkl")
    job_df.to_csv("job_data.csv", index=False, columns=columns)

    print("Job data has been saved to 'job_data.csv' and 'job_data.pkl'.")

# Main execution
try:
    email = "ksaikarthik12@gmail.com"
    password = "Mobile12345="

    login(email, password)
    switch_to_headless()
    process_all_jobs()
finally:
    driver.quit()
