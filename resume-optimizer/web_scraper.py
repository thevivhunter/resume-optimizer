from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)

def extract_job_position(text):
    job_keywords = ["engineer", "manager", "supervisor", "developer", "analyst", "director", "specialist", "coordinator", "consultant", "lead", "head"]
    doc = nlp(text)

    candidates = []

    # 1. Noun chunks
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.strip()
        if any(keyword in chunk.text.lower() for keyword in job_keywords):
            candidates.append(chunk_text)

    # 2. Named entities
    for ent in doc.ents:
        if any(keyword in ent.text.lower() for keyword in job_keywords):
            candidates.append(ent.text.strip())

    # 3. Dependency tree fallback
    for token in doc:
        if any(keyword in token.lemma_.lower() for keyword in job_keywords):
            subtree = " ".join([t.text for t in token.subtree]).strip()
            candidates.append(subtree)

    # Deduplicate and rank by length
    if candidates:
        unique_candidates = list(dict.fromkeys(candidates))  # Preserve order
        # Filter and sort by length
        valid_candidates = [
            c for c in unique_candidates
            if any(keyword in c.lower() for keyword in job_keywords)
        ]
        if valid_candidates:
            return max(valid_candidates, key=len).strip()

    return "Job position not identified"

def scrape_job_details_with_nlp_fallback(url):
    try:
        options = Options()
        options.headless = False  # Set True later for speed
        driver = webdriver.Firefox(options=options)

        driver.get(url)

        # ⏳ Wait up to 15 seconds for the job title (h1) to appear
        wait = WebDriverWait(driver, 15)
        h1_element = wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "h1"))
        )
        job_title = h1_element.text.strip()

        print(f"✅ Found job title via H1: {job_title}")
        driver.quit()
        return {"title": job_title}

    except Exception as e:
        print(f"❌ H1 not found: {e}")
        # Fallback: get full page text and use NLP
        try:
            page_text = driver.page_source
            soup = BeautifulSoup(page_text, 'html.parser')
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            text_content = soup.get_text(separator=" ", strip=True)
            driver.quit()
            job_title = extract_job_position(text_content)
            return {"title": job_title}
        except Exception:
            driver.quit()
            return {"title": "Job position not identified"}
        

url = input("Enter the URL: ")
details = scrape_job_details_with_nlp_fallback(url)
print("Job Details:", details)