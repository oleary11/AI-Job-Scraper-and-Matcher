import csv
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

# Initialize models
model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = pipeline("ner", model="dslim/bert-base-NER")  # Named Entity Recognition pipeline

# Define your profile preferences
profile_text = """
I am interested in software development roles, especially those involving Python, C#, or JavaScript.
I also have an interest in cybersecurity and tech sales. I am looking for positions that are entry to mid-level.
"""
profile_embedding = model.encode(profile_text, convert_to_tensor=True)

# Path to your ChromeDriver
chrome_driver_path = r"C:\SeleniumDrivers\chromedriver.exe"
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)

# Load company and job page URLs from CSV
job_page_links = []
with open("test.csv", mode="r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    job_page_links = [(row[0], row[2]) for row in reader]

# List to store matched jobs
matched_jobs = []

# AI-based function to identify job titles and descriptions
def find_job_titles_and_descriptions(text):
    job_titles = []
    job_descriptions = []

    # Use Named Entity Recognition to find potential job titles
    entities = nlp(text)
    for entity in entities:
        if entity['entity'] == 'B-TITLE':  # Assume B-TITLE indicates job title
            job_titles.append(entity['word'])

    # Use some heuristic to extract description around detected titles
    for title in job_titles:
        start_index = text.find(title)
        if start_index != -1:
            # Extract nearby text as the job description
            description_snippet = text[start_index:start_index + 500]  # Adjust length as needed
            job_descriptions.append(description_snippet)

    return list(zip(job_titles, job_descriptions))

# Process each company jobs page
for company_name, jobs_page_url in job_page_links:
    print(f"Scraping jobs from {company_name}: {jobs_page_url}")
    driver.get(jobs_page_url)
    time.sleep(2)  # Adjust as necessary or use WebDriverWait

    # Extract all visible text from the page
    page_text = driver.find_element(By.TAG_NAME, "body").text

    # Use AI to identify job titles and descriptions
    job_listings = find_job_titles_and_descriptions(page_text)

    # Compute similarity scores and filter top matches
    for job_title, job_description in job_listings:
        job_text = f"{job_title}\n{job_description}"
        job_embedding = model.encode(job_text, convert_to_tensor=True)
        similarity_score = util.pytorch_cos_sim(profile_embedding, job_embedding).item()

        if similarity_score > 0.5:  # Adjust threshold as needed
            matched_jobs.append({
                "company": company_name,
                "title": job_title,
                "description": job_description,
                "url": jobs_page_url,
                "similarity_score": similarity_score
            })

# Close the browser
driver.quit()

# Sort matched jobs by similarity score
matched_jobs = sorted(matched_jobs, key=lambda x: x['similarity_score'], reverse=True)

# Save matched jobs to a CSV file
csv_file = "matched_jobs.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Company", "Job Title", "Description", "URL", "Similarity Score"])  # Header
    for job in matched_jobs:
        writer.writerow([job["company"], job["title"], job["description"][:200] + "...", job["url"], f"{job['similarity_score']:.4f}"])

print(f"Matched jobs have been saved to {csv_file}")

# Display the top matches for immediate review
for match in matched_jobs[:10]:  # Display top 10 matches
    print(f"Company: {match['company']}")
    print(f"Job Title: {match['title']}")
    print(f"Description: {match['description'][:200]}...")  # Truncated for readability
    print(f"URL: {match['url']}")
    print(f"Similarity Score: {match['similarity_score']:.4f}")
    print("-" * 40)