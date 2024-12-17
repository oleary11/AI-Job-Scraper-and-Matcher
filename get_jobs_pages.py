import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Path to your ChromeDriver
chrome_driver_path = r"C:\SeleniumDrivers\chromedriver.exe"

# Set up the Chrome driver in headless mode for faster performance
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)

# List to store company name, company URL, and Jobs page URL
job_page_links = []

# Load company links from CSV
with open("company_links.csv", mode="r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    company_links = [(row[0], row[1]) for row in reader]

# Loop through each company link to extract the "Jobs page" URL
for company_name, company_url in company_links:
    driver.get(company_url)
    
    try:
        # Use WebDriverWait to wait for the "Jobs page" label and anchor to be present
        label_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//label[contains(text(), 'Jobs page:')]"))
        )
        job_page_element = label_element.find_element(By.XPATH, "./following-sibling::a")
        job_page_url = job_page_element.get_attribute("href")
        
        job_page_links.append((company_name, company_url, job_page_url))
        print(f"Found jobs page for {company_name}: {job_page_url}")
    
    except Exception as e:
        print(f"No jobs page found for {company_name} - {company_url}")

# Close the browser
driver.quit()

# Save the job page links to a new CSV file
csv_file = "job_page_links.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Company Name", "Company URL", "Jobs Page URL"])  # Header
    writer.writerows(job_page_links)

print(f"Job page links have been saved to {csv_file}")