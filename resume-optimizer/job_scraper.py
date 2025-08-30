# job_scraper.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import spacy
import re
import json
import csv
import time
from urllib.parse import urlparse

# Load NLP model
nlp = spacy.load("en_core_web_sm")

class JobScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.job_data = {}

    def start_driver(self):
        options = Options()
        options.headless = self.headless
        self.driver = webdriver.Firefox(options=options)
        return self.driver

    def detect_platform(self, url):
        """Detect job board platform to apply correct logic."""
        parsed = urlparse(url)
        hostname = parsed.netloc.lower()

        if "workable.com" in hostname:
            return "workable"
        elif "greenhouse.io" in hostname or "greenhouse.io" in url:
            return "greenhouse"
        elif "lever.co" in hostname:
            return "lever"
        elif "linkedin.com" in hostname:
            return "linkedin"
        else:
            return "generic"

    def extract_with_selectors(self, platform):
        """Use platform-specific selectors."""
        wait = WebDriverWait(self.driver, 15)

        selectors = {
            "workable": {
                "title": (By.TAG_NAME, "h1"),
                "location": (By.CSS_SELECTOR, "[data-ui=location]"),
                "department": (By.CSS_SELECTOR, "[data-ui=department]"),
                "company": (By.CSS_SELECTOR, ".company-title"),
                "description": (By.CSS_SELECTOR, ".description")
            },
            "greenhouse": {
                "title": (By.CSS_SELECTOR, "h1"),
                "location": (By.CSS_SELECTOR, ".location"),
                "department": (By.CSS_SELECTOR, ".dept"),
                "company": (By.CSS_SELECTOR, ".company-name"),
                "description": (By.ID, "job-desc")
            },
            "lever": {
                "title": (By.CSS_SELECTOR, "h2.posting-title"),
                "location": (By.CSS_SELECTOR, ".location"),
                "department": (By.CSS_SELECTOR, ".department"),
                "company": (By.CSS_SELECTOR, "h1.company-name"),
                "description": (By.CLASS_NAME, "section.page-centered")
            },
            "linkedin": {
                "title": (By.CSS_SELECTOR, "h1"),
                "location": (By.CSS_SELECTOR, "[data-automation-location='true']"),
                "department": (By.XPATH, "//h3[text()='Department']/following-sibling::span"),
                "company": (By.CSS_SELECTOR, "a[data-tracking-control-name='public_jobs_company-name']"),
                "description": (By.CSS_SELECTOR, "#job-details")
            }
        }

        config = selectors.get(platform, selectors["workable"])  # fallback
        data = {}

        for field, (by, selector) in config.items():
            try:
                element = wait.until(EC.visibility_of_element_located((by, selector)))
                data[field] = element.text.strip()
            except:
                data[field] = "Not found"
        return data

    def extract_with_nlp_fallback(self):
        """Fallback: extract title using NLP and regex."""
        page_text = self.driver.page_source
        soup = BeautifulSoup(page_text, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(" ", strip=True)

        # Try regex first
        regex_title = self.extract_with_regex(text)
        if regex_title:
            return regex_title

        # Then NLP
        return self.extract_job_position(text)

    def extract_with_regex(self, text):
        pattern = r'\b(?:Senior|Junior|Lead|Principal|Junior|Mid-level|Entry-level|Staff)?\s*(?:\w+\s)*?(?:Engineer|Manager|Supervisor|Developer|Analyst|Director|Specialist|Consultant|Architect|Coordinator|Head|Administrator|Scientist)\b'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches[0].strip() if matches else None

    def extract_job_position(self, text):
        job_keywords = ["engineer", "manager", "supervisor", "developer", "analyst", "director", "specialist", "consultant", "lead", "head", "architect", "coordinator"]
        doc = nlp(text)
        candidates = []

        for chunk in doc.noun_chunks:
            if any(keyword in chunk.text.lower() for keyword in job_keywords):
                candidates.append(chunk.text.strip())

        for ent in doc.ents:
            if any(keyword in ent.text.lower() for keyword in job_keywords):
                candidates.append(ent.text.strip())

        for token in doc:
            if any(keyword in token.lemma_.lower() for keyword in job_keywords):
                candidates.append(" ".join([t.text for t in token.subtree]).strip())

        if candidates:
            valid = [c for c in dict.fromkeys(candidates) if any(k in c.lower() for k in job_keywords)]
            return max(valid, key=len) if valid else "Job position not identified"
        return "Job position not identified"

    def scrape(self, url):
        """Main scrape method."""
        self.start_driver()
        try:
            self.driver.get(url)
            platform = self.detect_platform(url)
            print(f"🌐 Detected platform: {platform.upper()}")

            # Wait for page to load
            time.sleep(2)  # Small buffer

            # Try structured extraction
            try:
                data = self.extract_with_selectors(platform)
                title = data.get("title", "Not found")
                if "not found" not in title.lower():
                    self.job_data = {
                        "title": title,
                        "company": data.get("company", "Not found"),
                        "location": data.get("location", "Not found"),
                        "department": data.get("department", "Not found"),
                        "description": data.get("description", "")[:500] + "..."  # preview
                    }
                    print(f"✅ Extracted via selectors: {self.job_data['title']}")
                else:
                    raise Exception("No valid title found")
            except Exception as e:
                print(f"⚠️  Selector failed: {e}")
                print("🔁 Falling back to NLP...")
                fallback_title = self.extract_with_nlp_fallback()
                self.job_data = {
                    "title": fallback_title,
                    "company": "Not found",
                    "location": "Not found",
                    "department": "Not found",
                    "description": "N/A (fallback mode)"
                }

        except Exception as e:
            print(f"❌ Scrape failed: {e}")
            self.job_data = {
                "title": "Scraping failed",
                "company": "N/A",
                "location": "N/A",
                "department": "N/A",
                "description": str(e)
            }
        finally:
            self.driver.quit()

        return self.job_data

    def export_json(self, filename="job_data.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.job_data, f, indent=4, ensure_ascii=False)
        print(f"📁 Exported to {filename}")

    def export_csv(self, filename="job_data.csv", mode="a"):
        is_empty = not (open(filename, 'r').readline() if __import__('os').path.exists(filename) else None)
        with open(filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.job_data.keys())
            if is_empty:
                writer.writeheader()
            writer.writerow(self.job_data)
        print(f"📁 Exported to {filename}")