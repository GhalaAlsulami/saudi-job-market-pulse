import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load your secret keys from .env file
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# ── Settings ──────────────────────────────────────────────
COUNTRY = "gb"       # Adzuna uses "gb" as closest to Saudi Arabia coverage
                     # We filter by keyword "Saudi" or remote roles
RESULTS_PER_PAGE = 50
MAX_PAGES = 5        # 5 pages x 50 results = up to 250 jobs per run
KEYWORDS = "data analyst"   # Change this to any tech role you want to track

# ── Main fetch function ────────────────────────────────────
def fetch_jobs(keyword=KEYWORDS, max_pages=MAX_PAGES):
    """
    Fetches job listings from Adzuna API.
    Returns a list of job dictionaries.
    """
    all_jobs = []

    print(f"\n🔍 Fetching jobs for: '{keyword}'")
    print(f"📅 Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    for page in range(1, max_pages + 1):
        url = (
            f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{page}"
            f"?app_id={APP_ID}"
            f"&app_key={APP_KEY}"
            f"&results_per_page={RESULTS_PER_PAGE}"
            f"&what={keyword.replace(' ', '%20')}"
            f"&content-type=application/json"
        )

        response = requests.get(url)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"❌ Error on page {page}: {response.status_code}")
            break

        data = response.json()
        jobs = data.get("results", [])

        if not jobs:
            print(f"✅ No more results after page {page - 1}")
            break

        # Extract only the fields we care about
        for job in jobs:
            cleaned_job = {
                "id":          job.get("id", ""),
                "title":       job.get("title", ""),
                "company":     job.get("company", {}).get("display_name", "Unknown"),
                "location":    job.get("location", {}).get("display_name", "Unknown"),
                "description": job.get("description", ""),
                "salary_min":  job.get("salary_min", None),
                "salary_max":  job.get("salary_max", None),
                "category":    job.get("category", {}).get("label", ""),
                "created":     job.get("created", ""),
                "url":         job.get("redirect_url", ""),
                "fetched_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            all_jobs.append(cleaned_job)

        print(f"✅ Page {page}: fetched {len(jobs)} jobs (total so far: {len(all_jobs)})")

    print("-" * 50)
    print(f"🎉 Done! Total jobs fetched: {len(all_jobs)}")
    return all_jobs


# ── Save to JSON (temporary — later we save to PostgreSQL) ─
def save_to_json(jobs, filename=None):
    """
    Saves jobs to a JSON file inside the data/ folder.
    We use JSON for now — in Phase 2 this becomes PostgreSQL.
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/jobs_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved {len(jobs)} jobs to {filename}")
    return filename


# ── Run it ─────────────────────────────────────────────────
if __name__ == "__main__":
    # Fetch jobs
    jobs = fetch_jobs(keyword="data analyst")

    # Print first job so we can see what the data looks like
    if jobs:
        print("\n📋 Sample job (first result):")
        print(json.dumps(jobs[0], indent=2))

    # Save to JSON file
    save_to_json(jobs)
