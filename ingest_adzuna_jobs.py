import os
import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

url = "https://api.adzuna.com/v1/api/jobs/us/search/1"

params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "what": "Data Engineer",
    "where": "Florida",
    "results_per_page": 10,
    "content-type": "application/json"
}

response = requests.get(url, params=params, timeout=30)

response.raise_for_status()

data = response.json()

print("Total matching jobs:", data.get("count"))
print("Jobs retrieved:", len(data.get("results", [])))

# Inspect one job
if data.get("results"):
    print("\nFirst job:")
    print(data["results"][0])