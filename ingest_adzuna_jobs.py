import os
import requests
from dotenv import load_dotenv
import json
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import boto3

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search"

SEARCH_PARAMS = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "what": "Data Engineer",
    "where": "Florida",
    "results_per_page": 10,
    "max_days_old": 2,
    "sort_by": "date",
    "sort_direction": "down",
    "content-type": "application/json"
}

S3_BUCKET = "job-market-intelligence-raw-lr"

session = boto3.Session(
    profile_name="job-market",
    region_name="us-east-2"
)

s3_client = session.client("s3")

#response = requests.get(url, params=params, timeout=30)

#response.raise_for_status()

#data = response.json()

#print("Total matching jobs:", data.get("count"))
#print("Jobs retrieved:", len(data.get("results", [])))

def results_analysis(data):
    # return 10 jobs and save them to a file for inspection and data fields check
    if data.get("results"):
        print(data["results"][0]) 
        first_job = data["results"][0]
        for field in first_job:
            print(field)
        output_path = Path(__file__).resolve().parent / "data" / "jobs.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as f:
            json.dump(data["results"], f)
    '''
    title -> job title analysis
    location -> geographical location analysis
    'location': {'area': ['US', 'Florida', 'Hillsborough County', 'Tampa'] -> nested objects
    adref
    created -> posting date / how fresh is the job posting
    'created': '2026-11-10T04:36:58Z'
    salary_is_predicted -> estimated vs advertised salary
    redirect_url -> original job posting url
    company -> employer
    'company': {'__CLASS__': 'Adzuna::API::Response::Company', 'display_name': 'Vaco LLC'} -> nested objects
    latitude
    id
    longitude
    salary_max -> salary analysis
    category -> job classification
    'category': {'label': 'IT Jobs', 'tag': 'it-jobs', '__CLASS__': 'Adzuna::API::Response::Category'}
    salary_min -> salary analysis
    description -> jb, skill extraction
    '''

def fetch_page(page_number):
    url = f"{BASE_URL}/{page_number}"
    response = requests.get(url, params=SEARCH_PARAMS, timeout=30)
    response.raise_for_status()
    return response.json()

def ingest_jobs(max_pages=3):
    timestamp = datetime.now(timezone.utc)
    date = timestamp.strftime("%Y-%m-%d")
    run_id = timestamp.strftime("%Y%m%d%H%M%S")
    #output_dir = Path(__file__).resolve().parent / "data" / date
    #output_dir.mkdir(parents=True, exist_ok=True)
    total_jobs = 0
    pages_processed = 0
    for page in range(1, max_pages + 1):
        print(f"Fetching page {page}...")
        data = fetch_page(page)
        jobs = data.get("results", [])
        total_jobs += len(jobs)
        pages_processed += 1
        if not jobs:
            print("No more jobs found.")
            break
        output_file = f"{date}_run{run_id}_page{page}.json"
        #with output_file.open("w") as f:
        #    json.dump(jobs, f)
        # when with block is exited, it automatically closes the file, this ensures all data has been written before boto3 starts reading it for upload    
        s3_key = (
            f"adzuna/ingestion_date={date}/"
            f"{output_file}"
        )

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(jobs),
            ContentType="application/json"
        )

        print(f"Uploaded to S3: {s3_key}")
        print(f"Saved: {output_file}")
    print(f"Job ingestion completed. (Total jobs: {total_jobs}, Pages processed: {pages_processed})")

# convert nested job record into a flat record  
def transform_jobs(job, ingestion_date):
    location = job.get("location", {})
    company = job.get("company", {})
    category = job.get("category", {})
    area = location.get("area", [])
    # area[0] - Country (US)
    # area[1] - State (Florida)
    # area[2] - County (Hillsborough County)
    # area[3] - City (Tampa)
    return {
        "id": job.get("id"),
        "title": job.get("title"),
        "description": job.get("description"),
        "location": location.get("display_name"),
        "area": area,
        "latitude": job.get("latitude"),
        "longitude": job.get("longitude"),
        "country": area[0] if len(area) > 0 else None,
        "state": area[1] if len(area) > 1 else None,
        "county": area[2] if len(area) > 2 else None,
        "city": area[3] if len(area) > 3 else None,
        "company_name": company.get("display_name"),
        "category_label": category.get("label"),
        "category_tag": category.get("tag"),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "salary_is_predicted": job.get("salary_is_predicted"),
        "created": job.get("created"),
        "redirect_url": job.get("redirect_url"),
        "adref": job.get("adref"),
        "ingestion_date": ingestion_date
    }
    

if __name__ == "__main__":
    if not APP_ID or not APP_KEY:
        raise ValueError("Missing Adzuna API credentials")

    ingest_jobs(max_pages=5)
    
    #all_jobs = []
    # load all json files from data directory, regardless of date
    #data_dir = Path(__file__).resolve().parent / "data"
    #for json_file in data_dir.glob("**/*.json"):
    #    with json_file.open("r") as f:
    #        jobs = json.load(f)
    #        ingestion_date = json_file.parent.name  # date folder name
    #        for job in jobs:
    #            all_jobs.append(transform_jobs(job, ingestion_date))
    #df = pd.DataFrame(all_jobs)
    #print(df.head())
    #df.to_csv(data_dir / "all_jobs.csv", index=False)
    #print("Saved transformed job data to all_jobs.csv")
   
