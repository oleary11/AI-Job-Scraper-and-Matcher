import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

# Path to your ChromeDriver
chrome_driver_path = r"C:\SeleniumDrivers\chromedriver.exe"

# Set up the Chrome driver
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

# Initialize an empty list to store company links
company_links = []

# Loop through pages 1 to 5
for page_num in range(1, 6):
    url = f"https://gregslist.com/phoenix/search/?filtered=true&paged={page_num}"
    driver.get(url)
    
    # Wait for the page to load
    time.sleep(2)
    
    try:
        # Adjusting selector based on observed structure on the site
        # Find company listings in each page
        listings = driver.find_elements(By.CLASS_NAME, "company-listing")  # Update if needed
        
        for listing in listings:
            link_element = listing.find_element(By.TAG_NAME, "a")
            company_name = link_element.text
            company_url = link_element.get_attribute("href")
            company_links.append((company_name, company_url))
            print(f"Found company: {company_name} - {company_url}")
    
    except Exception as e:
        print(f"Error on page {page_num}: {e}")

# Close the browser
driver.quit()

# Save company_links to a CSV file
csv_file = "company_links.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Company Name", "Company URL"])  # Header
    writer.writerows(company_links)

print(f"Company links have been saved to {csv_file}")