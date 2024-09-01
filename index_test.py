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
        # Disable images and CSS for faster loading
        prefs = {"profile.managed_default_content_settings.images": 2,
                 "profile.managed_default_content_settings.stylesheets": 2,
                 "profile.managed_default_content_settings.javascript": 1}
        options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

simplify_url = "https://simplify.jobs/jobs?state=United%20States&points=71.5388001%3B-66.885417%3B18.7763%3B-180&country=United%20States&experience=Internship%3BEntry%20Level%2FNew%20Grad%3BJunior%3BMid%20Level&category=Operations%20%26%20Logistics%3BCustomer%20Success%20Management%3BIT%20%26%20Security%3BCustomer%20Success%20%26%20Support%3BMechanical%20Engineering%3BMedical%2C%20Clinical%20%26%20Veterinary%3BEngineering%20Management%3BLegal%20%26%20Compliance%3BElectrical%20Engineering%3BSupply%20Chain%20Management%3BPeople%20%26%20HR%3BCybersecurity%3BCustomer%20Support%3BConsulting%3BHuman%20Resources%3BContent%20%26%20Writing%3BStrategy%20Development%3BSolution%20Engineering%3BLegal%3BManagement%20Consulting%3BAerospace%20Engineering%3BManufacturing%20Engineering%3BBiology%20%26%20Biotech%3BHealthcare%20Administration%20%26%20Support%3BEmbedded%20Engineering%3BElectronics%20Design%20Engineering%3BArchitecture%20%26%20Civil%20Engineering%3BAdministrative%20%26%20Executive%20Assistance%3BMechanical%20Maintenance%20and%20Reliability%20Engineering%3BLab%20%26%20Research%3BContent%20Strategy%3BNursing%20%26%20Allied%20Health%20Professionals%3BIT%20Support%3BRisk%20%26%20Compliance%3BCustomer%20Success%3BReal%20Estate%3BAdministrative%20Support%3BHardware%20Engineering%3BDesign%20Engineering%3BProcurement%20%26%20Sourcing%3BBiology%20Lab%20%26%20Research%3BResearch%20%26%20Development%3BSite%20Reliability%20Engineering%3BIT%20Project%20Management%3BLife%20Sciences%3BPhysicians%20%26%20Surgeons%3BRisk%20Management%3BPR%20%26%20Communications%3BIT%20%26%20Support%3BIT%20Consulting%3BSystems%20Engineering%20Management%3BGame%20Engineering%3BTechnical%20Writing%3BConstruction%20Management%3BPower%20Systems%20Engineering%3BSystem%20Administration%3BInventory%20Management%3BPlatform%20Engineering%3BSecurity%20Engineering%3BInsurance%3BRobotics%20and%20Automation%20Engineering%3BCopywriting%3BContract%20Management%3BNetwork%20Administration%3BControl%20Systems%20Engineering%3BVeterinary%20Professionals%3BAuditing%3BTechnical%20Recruiting%3BQuantitative%20Research%3BExecutive%20Support%3BWarehouse%20Operations%3BJournalism%3BPublic%20Health%3BThermal%20and%20Fluid%20Systems%20Engineering%3BElectronic%20Hardware%20Engineering%3BInstrumentation%20and%20Measurement%20Engineering%3BTransportation%20Engineering%3BMaterials%20%26%20Structures%3BEmbedded%20Systems%20Engineering%3BComputational%20Biology%3BStructural%20Engineering%3BHardware%20Validation%20%26%20Testing%3BCreative%20Writing%3BDigital%20Journalism%3BPropulsion%3BBioinformatics%3BEnvironmental%20Engineering%3BQuantitative%20Analysis%3BBookkeeping%3BRF%20and%20Microwave%20Engineering%3BRobotics%20%26%20Autonomous%20Systems%3BAlgorithm%20Development%3BEditing%20%26%20Proofreading%3BMedical%20Research%3BEnvironmental%20Sciences%3BAutomation%20Testing%3BSpace%20%26%20Rocket%20Engineering%3BComputer%20Hardware%20Engineering%3BAvionics%3BCustomer%20Experience%3BArchitectural%20Design%3BDiagnostics%20%26%20Laboratory%20Professionals%3BInterdisciplinary%20Research%3BGenomics%3BCustomer%20Education%20%26%20Training%3BFlight%20Dynamics%3BNetwork%20Engineering%3BTreasury%3BPrivate%20Equity%3BStrategy%20Consulting%3BSystem%20Hardware%20Engineering%3BSpecialized%20Administrative%20Roles%3BManagement%20Accounting%3BEnvironmental%20Consulting%3BCost%20Accounting%3BWater%20Resources%20Engineering%3BSecurity%20Engineering%20Management%3BOperations%20Consulting%3BCopywriting%20Marketing%3BIntellectual%20Property%20(IP)%3BBuilding%20Services%20Engineering%3BStrategy%20Research%3BTelecommunications%20Engineering%3BAutomotive%20Electrical%20Engineering%3BNews%20Reporting%3BGeotechnical%20Engineering%3BMicroelectronics%20Engineering%3BSignal%20Processing%20Engineering%3BMechanical%20Hardware%20Engineering%3BTransportation%20%26%20Distribution%3BCustomer%20Service%20%26%20Reception%3BVenture%20Capital%3BAdministration%3BPerformance%20Testing%3BInternational%20Accounting%3BAerodynamics%3BServer%20Administration%3BGeneralist%20Recruiting%3BInvestigative%20Journalism%3BPhysical%20Sciences%3BReal%20Estate%20Marketing%3BUrban%20Planning%3BLegal%20Consulting%3BIndustrial%20Design%3BForensic%20Accounting%3BBroadcast%20Journalism%3BSecurity%20Testing%3BGovernmental%20Accounting%3BStoryboarding%3BTreasury%20Accounting%3BFeature%20Writing%3BEnvironmental%20Accounting%3BScheduling%20%26%20Travel%20Coordination"
job_category = "Other"

# Initialize driver in non-headless mode for login
driver = initialize_driver(headless=False)
first_flag = True

# Helper function to wait for an element
def wait_for_element(by, value, timeout=5):
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return element
    except Exception as e:
        print(f"Error waiting for element {value}")
        return None

# Function to login
def login(email, password):
    driver.get("https://simplify.jobs/auth/login")
    email_element = wait_for_element(By.ID, "email")
    email_element.send_keys(email)
    
    password_element = wait_for_element(By.ID, "password")
    password_element.send_keys(password)
    
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()
    
    input("Please solve the CAPTCHA if present and press Enter to continue...")

    if driver.current_url == "https://simplify.jobs/dashboard":
        print("Login successful")
        driver.get(simplify_url)
        time.sleep(5)

def generate_unique_id(input_string):
    return hashlib.sha256(input_string.encode('utf-8')).hexdigest()

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

# Function to extract job details
def extract_job_details():
    job_details = {}
    try:
        company_element = wait_for_element(By.XPATH, "//div[@class='flex items-center gap-2']/p", timeout = 20)
        job_details['company'] = company_element.text
        
        location_element = wait_for_element(By.XPATH, "//div[@class='flex items-center gap-2']//p[@class='text-sm font-bold']")
        job_details['location'] = location_element.text

        title_element = wait_for_element(By.XPATH, "//div[@class='pb-2']/p[@class='text-left text-xl font-bold text-secondary-400']")
        posted_at_element = wait_for_element(By.XPATH, "//div[@class='pb-2']/p[@class='mt-1 text-left text-sm text-gray-500']")
        job_details['title'] = title_element.text
        job_details['country'] = "United States"
        
        posted_at_text = posted_at_element.text.replace("Posted on ", "").replace("Updated on ", "")
        job_details['posted_at'] = datetime.now().strftime('%Y-%m-%d') if "Confirmed live in the last 24 hours" in posted_at_text else datetime.strptime(posted_at_text, '%m/%d/%Y').strftime('%Y-%m-%d')

        job_details['job_reference'] = generate_unique_id(job_details['title'] + job_details['company'] + job_details['location'])

        job_type_element = wait_for_element(By.XPATH, "//p[contains(@class, 'rounded-full bg-primary-50 px-4 py-2 text-sm text-primary-400')]")
        job_details['job_type'] = job_type_element.text

        company_logo_element = wait_for_element(By.XPATH, "//a[@class='flex size-[72px] shrink-0 items-start focus:outline-none']/img")
        job_details['company_logo'] = company_logo_element.get_attribute("src")

        company_website_element = wait_for_element(By.XPATH, "//a[contains(@class, 'flex items-center space-x-2') and contains(text(), 'Website')]")
        job_details['company_website'] = company_website_element.get_attribute("href")

        company_description_element = wait_for_element(By.XPATH, "//p[@class='mt-4 text-left text-sm text-secondary-400']")
        job_details['company_description'] = company_description_element.text

        job_description_element = wait_for_element(By.XPATH, "//div[contains(@class, 'prose prose-sm text-left hidden')]")
        job_details['description'] = job_description_element.get_attribute("innerHTML")

        try:
            compensation_element = driver.find_element(By.XPATH, "//p[contains(@class, 'text-base font-bold text-secondary-400')]")
            compensation_text = compensation_element.text

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
            time_frame_element = compensation_element.find_element(By.CSS_SELECTOR, 'p.text-base span')
            job_details['compensation_time_frame'] = time_frame_element.text
            job_details['compensation_currency'] = 'USD'
        
        except Exception as e:
            print("Compensation N/A")

        job_details['remote'] = 1 if "remote" in job_details['location'].lower() else 0
        job_details['category'] = job_category

    except Exception as e:
        print(f"Failed to extract job details")
        return job_details
    
    return job_details

# Function to handle job application process for a single job
def apply_for_job(first_job=False):
    retries = 5
    apply_button_clicked = False
    job_details = extract_job_details()
    if len(job_details)==0:
        return job_details
    for attempt in range(retries):
        try:
            apply_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Apply')]"))
            )
            print(f"Apply button found. Attempting to click (Attempt {attempt + 1}).")

            driver.execute_script("arguments[0].click();", apply_button)
            print("Apply button clicked using JavaScript.")
            apply_button_clicked = True

            if first_job:
                try:
                    checkbox = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.ID, "preventShow"))
                    )
                    checkbox.click()
                    print("Checked 'Don't show this popup again'.")

                    proceed_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Proceed anyway')]"))
                    )
                    proceed_button.click()
                    print("Clicked 'Proceed anyway'.")
                except Exception as e:
                    print("First-time popup did not appear or failed to interact with it:")

            try:
                WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                print("New tab opened successfully.")
                break
            except:
                print("New tab did not open, retrying...")
                continue

        except Exception as e:
            print(f"Failed to click the Apply button on attempt {attempt + 1}")

    if not apply_button_clicked or len(driver.window_handles) == 1:
        print("Failed to open new tab after 5 attempts. Skipping this job.")
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
    columns = ['location', 'title', 'country', 'job_type', 'posted_at', 'job_reference', 'company', 
               'company_logo', 'company_website', 'company_description', 'category', 'url', 
               'description', 'min_compensation', 'max_compensation', 'compensation_currency', 
               'compensation_time_frame', 'remote']
    job_data = []
    scroll_until_all_jobs_loaded()
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
            if isinstance(job_details,type(None)) or len(job_details)==0:
                print(f"Skipping job {index + 1} of {len(job_cards)}")
                continue
            job_data.append(job_details)

        except Exception as e:
            print(f"Error processing job {index + 1}")
            time.sleep(2)

    job_df = pd.DataFrame(job_data, columns = columns)
    job_df.to_pickle("job_data.pkl")
    job_df.to_csv("job_data.csv", index=False, columns = columns)

# Main execution
try:
    email = "ksaikarthik12@gmail.com"
    password = "Mobile12345="

    login(email, password)
    switch_to_headless()
    process_all_jobs()
finally:
    driver.quit()
