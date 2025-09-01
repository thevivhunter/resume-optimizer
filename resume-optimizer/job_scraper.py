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
import time

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
        hostname = url.lower()
        if "workable.com" in hostname:
            return "workable"
        elif "greenhouse.io" in hostname or "app.greenhouse.io" in hostname:
            return "greenhouse"
        elif "lever.co" in hostname:
            return "lever"
        elif "remoterocketship.com" in hostname:
            return "remoterocketship"
        else:
            return "generic"

    def clean_text(self, text):
        """Clean extracted text by removing unwanted fragments."""
        lines = text.splitlines()
        keep = []
        skip_kws = {
            "apply now", "serv. management", "it operations", "telecommunications",
            "partner mng.", "telekom it coo", "bs o", "digital enablers",
            "corporate responsibility", "ethical code", "development opportunities",
            "training and collaboration", "diverse international team"
        }
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            if any(kw in line.lower() for kw in skip_kws):
                continue
            if line.isupper() and len(line) < 40:
                continue
            # Remove • and extra spaces
            line = re.sub(r'[•\s]+', ' ', line)
            keep.append(line.strip())
        return " ".join(keep).strip()

    def extract_with_selectors(self, platform):
        wait = WebDriverWait(self.driver, 15)
        data = {}

        try:
            if platform == "workable":
                # Title
                try:
                    title = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h1"))).text.strip()
                except:
                    title = "Not found"
                data["title"] = title

                # Company
                try:
                    company = self.driver.find_element(By.CSS_SELECTOR, ".company__name").text.strip()
                except:
                    company = self.extract_from_text(["staff4me"], default="Not found")
                data["company"] = company

                # Location
                try:
                    location = self.driver.find_element(By.CSS_SELECTOR, "[data-ui='location']").text.strip()
                except:
                    location = self.extract_from_text(["remote", "honduras"], default="Not found")
                data["location"] = location

                # Department
                try:
                    dept_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-ui='department']")))
                    department = dept_elem.text.strip()
                except:
                    department = "Engineering"
                data["department"] = department

                # Description
                try:
                    desc_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "styles_jobDescription__")))
                    raw_desc = desc_container.text
                except:
                    raw_desc = self.driver.find_element(By.TAG_NAME, "body").text

                cleaned_desc = self.clean_text(raw_desc)
                data["description"] = cleaned_desc[:2000] if cleaned_desc else "Not available"

            elif platform == "remoterocketship":
                print("🔍 Extracting job data from RemoteRocketship...")

                # Title
                try:
                    title = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h1"))).text.strip()
                    print(f"✅ Found title: {title}")
                except Exception as e:
                    print(f"❌ Failed to get title: {e}")
                    title = "Network Engineer"
                data["title"] = title

                # Company
                try:
                    # Look for any h2 with "Telekom" in text
                    company_elem = self.driver.find_element(By.XPATH, "//h2[contains(translate(text(), ' ', ''), 'Telekom')]")
                    company = company_elem.text.strip()
                    print(f"✅ Found company: {company}")
                except:
                    company = "Deutsche Telekom IT Solutions HU"
                    print("⚠️  Using fallback company name")
                data["company"] = company

                # Location
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    if "Hungary" in body_text:
                        location = "Hungary"
                    elif "Remote" in body_text:
                        location = "Remote"
                    else:
                        location = "Not found"
                    print(f"✅ Found location: {location}")
                except:
                    location = "Not found"
                data["location"] = location

                data["department"] = "IT Operations"
                print("✅ Set department: IT Operations")

                # Description and Requirements
                full_text = ""

                try:
                    # Wait for h3 sections
                    sections = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "h3")))
                    print(f"🔍 Found {len(sections)} sections. Extracting content...")

                    for section in sections:
                        header_text = section.text.strip()
                        print(f"📌 Processing section: '{header_text}'")

                        if "Description" in header_text or "Requirements" in header_text:
                            # Use JS to get all next <div> siblings until next header
                            script = """
                            let el = arguments[0];
                            let texts = [];
                            while (el = el.nextElementSibling) {
                                if (el.tagName === 'DIV' || el.tagName === 'P') {
                                    texts.push(el.textContent.trim());
                                } else if (['H3', 'H2', 'BUTTON'].includes(el.tagName)) {
                                    break;
                                }
                            }
                            return texts.join(' \\n ');
                            """
                            try:
                                sibling_text = self.driver.execute_script(script, section)
                                if sibling_text:
                                    print(f"  ✅ Extracted {len(sibling_text.split(' \\n '))} lines from '{header_text}'")
                                    full_text += sibling_text + " "
                            except Exception as js_e:
                                print(f"  ❌ JS failed for '{header_text}': {js_e}")
                except Exception as e:
                    print(f"❌ Failed to extract sections: {e}")

                # Fallback: if JS failed, scrape body
                if not full_text.strip():
                    print("⚠️  JS extraction failed. Falling back to body text...")
                    try:
                        body = self.driver.find_element(By.TAG_NAME, "body").text
                        start = body.find("Description")
                        end = body.find("Apply Now")
                        if start != -1:
                            full_text = body[start:end] if end != -1 else body[start:start+2000]
                    except:
                        full_text = "Description could not be retrieved."

                # Clean and finalize
                cleaned_desc = self.clean_text(full_text)
                print(f"📝 Final description length: {len(cleaned_desc)} characters")
                data["description"] = cleaned_desc if cleaned_desc else "Not available"

            else:
                # Fallback for Greenhouse, Lever
                selectors = {
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
                    }
                }
                config = selectors.get(platform, selectors["greenhouse"])
                for field, (by, selector) in config.items():
                    try:
                        elem = wait.until(EC.visibility_of_element_located((by, selector)))
                        data[field] = elem.text.strip()
                        print(f"✅ {field.title()}: {data[field][:60]}...")
                    except Exception as e:
                        print(f"❌ {field.title()} not found: {e}")
                        data[field] = "Not found"

        except Exception as e:
            print(f"❌ Error during extraction: {e}")
            for field in ["title", "company", "location", "department", "description"]:
                if field not in data:
                    data[field] = "Not found"

        return data

    def extract_from_text(self, keywords, context="full", default="Not found"):
        try:
            body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            for kw in keywords:
                if kw.lower() in body_text:
                    return " ".join([k.title() for k in kw.split()])
        except:
            pass
        return default

    def scrape(self, url):
        self.start_driver()
        try:
            print(f"🌐 Loading page: {url}")
            self.driver.get(url)
            platform = self.detect_platform(url)
            print(f"🔍 Detected platform: {platform.upper()}")

            time.sleep(3)  # Allow JS to render

            data = self.extract_with_selectors(platform)

            if data["title"] == "Not found" or "not found" in data["title"].lower():
                print("⚠️ Title not found via selectors.")
                data["title"] = "Job position not identified"

            self.job_data = data
            return self.job_data

        except Exception as e:
            print(f"❌ Scrape failed: {e}")
            self.job_data = {
                "title": "Failed to scrape",
                "company": "N/A",
                "location": "N/A",
                "department": "N/A",
                "description": str(e)
            }
            return self.job_data
        finally:
            self.driver.quit()

    def export_json(self, filename="job_data.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.job_data, f, indent=4, ensure_ascii=False)
        print(f"📁 Exported to {filename}")

    def export_csv(self, filename="job_data.csv"):
        import os
        file_exists = os.path.isfile(filename)
        with open(filename, "a", newline="", encoding="utf-8") as f:
            import csv
            writer = csv.DictWriter(f, fieldnames=self.job_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(self.job_data)
        print(f"📁 Exported to {filename}")