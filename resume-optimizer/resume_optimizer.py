# resume_optimizer.py
import os
import json
import csv
from job_scraper import JobScraper
import spacy
import re
from datetime import datetime, timedelta

# PDF parsing
import fitz  # PyMuPDF

# DOCX parsing
from docx import Document

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Enhanced skill keywords for Network Engineer (Deutsche Telekom)
SKILL_KEYWORDS = {
    "technical": [
        "python", "aws", "docker", "kubernetes", "git", "ci/cd", "sql", "linux", "unix",
        "networking", "firewall", "cisco", "vpn", "vlan", "routing", "switching",
        "active directory", "powershell", "scripting", "cybersecurity", "it support",
        "ccna", "ccnp", "ccie", "compliance", "migration", "infrastructure", "monitoring",
        "sdn", "aci", "apstra", "spine", "leaf", "fabric", "radius", "tacacs", "ldap",
        "traffic shaping", "subnet", "ipv4", "ipv6", "cloud", "loadbalancer", "cloud network",
        "authentication", "logging", "dns", "quotation", "tender", "procurement"
    ],
    "soft": [
        "leadership", "communication", "teamwork", "problem-solving", "project management",
        "time management", "collaboration", "adaptability", "analytical skills",
        "cooperative", "task-oriented", "detail-oriented", "matter-of-fact"
    ],
    "roles": [
        "network engineer", "engineer", "developer", "analyst", "administrator",
        "consultant", "architect", "coordinator", "director", "specialist"
    ]
}

# Blacklist generic or weak words
BLACKLIST = {
    "ability", "background", "bachelor", "degree", "experience", "role", "job",
    "team", "work", "skills", "position", "candidate", "individual", "excellent",
    "strong", "good", "help", "support", "make", "use", "perform", "carry out",
    "found", "url", "https", "error", "fetching", "description"
}


def read_resume(file_path):
    """Read resume text from PDF (PyMuPDF) or DOCX."""
    if not os.path.exists(file_path):
        print("❌ File not found.")
        return ""

    _, ext = os.path.splitext(file_path.lower())

    try:
        if ext == ".pdf":
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text("text")
            doc.close()
            return " ".join(text.split())

        elif ext == ".docx":
            doc = Document(file_path)
            return " ".join(para.text for para in doc.paragraphs)

        else:
            print("❌ Unsupported format. Use .pdf or .docx")
            return ""

    except Exception as e:
        print(f"❌ Error reading resume: {e}")
        return ""


def extract_keywords_from_text(text):
    doc = nlp(text.lower())
    return [
        token.lemma_ for token in doc
        if not token.is_stop and not token.is_punct and len(token.lemma_) > 2
    ]


def suggest_resume_keywords(job_title, job_description):
    full_text = (job_title + " " + job_description).lower()
    words = extract_keywords_from_text(full_text)

    suggestions = {
        "Technical Skills": [],
        "Soft Skills": [],
        "Roles": [],
        "Other Keywords": []
    }
    certifications = []

    for word in words:
        word_lower = word.lower()
        if word_lower in SKILL_KEYWORDS["technical"]:
            suggestions["Technical Skills"].append(word.title())
        elif word_lower in SKILL_KEYWORDS["soft"]:
            suggestions["Soft Skills"].append(word.title())
        elif word_lower in SKILL_KEYWORDS["roles"]:
            suggestions["Roles"].append(word.title())
        elif word.upper() in ["CCNA", "CCNP", "CCIE", "CISSP", "AWS", "AZURE", "GCP", "ITIL", "PMP"]:
            certifications.append(word.upper())
        elif word_lower not in BLACKLIST and re.match(r"^[a-z]{3,}$", word_lower):
            suggestions["Other Keywords"].append(word.title())

    for key in suggestions:
        suggestions[key] = sorted(list(set(suggestions[key])))

    return suggestions, certifications


def calculate_match_score(resume_text, job_description):
    resume_text = resume_text.lower()
    job_doc = nlp(job_description.lower())
    job_keywords = [
        token.lemma_ for token in job_doc
        if not token.is_stop and not token.is_punct and token.pos_ in ["NOUN", "PROPN"]
    ]

    seen = set()
    job_keywords = [k for k in job_keywords if not (k in seen or seen.add(k))]

    if not job_keywords:
        return 0, [], []

    matched = [k for k in job_keywords if k in resume_text]
    missing = [k for k in job_keywords if k not in resume_text]

    score = (len(matched) / len(job_keywords)) * 100 if job_keywords else 0
    return score, matched, missing
    

def save_application(app_data):
    """Safely append application to job_applications.json with error recovery."""
    try:
        file_path = "job_applications.json"
        apps = {"applications": []}

        # Read existing data only if file exists AND not empty
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        apps = json.loads(content)
                # Ensure it has the right structure
                if "applications" not in apps or not isinstance(apps["applications"], list):
                    apps = {"applications": []}
            except json.JSONDecodeError:
                print("⚠️  Corrupted job_applications.json. Creating new file.")
                apps = {"applications": []}

        # Generate ID
        app_id = f"app_{app_data['timestamp'].replace('-', '').replace(':', '').replace('.', '')}"
        app_data["id"] = app_id

        # Append and save
        apps["applications"].append(app_data)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(apps, f, indent=4, ensure_ascii=False)
        print("📄 Application saved to job_applications.json")

    except Exception as e:
        print(f"❌ Failed to save application: {e}")


def save_recommendations(job_data, suggestions, certs, missing_keywords, resume_path): 
    """Save keyword recommendations to a text file."""
    try:
        filename = "resume_recommendations.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("🎯 RESUME OPTIMIZATION RECOMMENDATIONS\n")
            f.write("="*60 + "\n\n")
            f.write(f"Job: {job_data['title']} @ {job_data['company']}\n")
            f.write(f"Resume: {os.path.basename(resume_path)}\n\n")

            if certs:
                f.write(f"🎖️  Add Certifications: {', '.join(certs)}\n\n")

            for category, terms in suggestions.items():
                if terms:
                    f.write(f"{category}:\n")
                    f.write("  " + ", ".join(terms) + "\n\n")

            if missing_keywords:
                f.write("💡 Keywords to Add to Resume:\n")
                f.write("  " + ", ".join([w.title() for w in missing_keywords[:10]]) + "...\n")

        print(f"📝 Recommendations saved to {filename}")
    except Exception as e:
        print(f"❌ Failed to save recommendations: {e}")

def optimize_resume_for_job(url):
    print("🔍 Resume Optimizer - Smart Job Keyword Analyzer")
    print("💡 Paste any job URL from Workable, Greenhouse, Lever, or LinkedIn\n")

    # Handle blocked or unknown sites
    if "linkedin.com" in url.lower() or "tecoloco.com" in url.lower():
        print("🔐 This site blocks scrapers. Please enter job details manually:")
        title = input("📌 Job Title: ").strip()
        company = input("🏢 Company: ").strip() or "Not specified"
        location = input("📍 Location: ").strip() or "Remote"
        description = input("📝 Paste job description: ").strip()

        job_data = {
            "title": title or "Unknown",
            "company": company,
            "location": location,
            "department": "IT Operations",
            "description": description or "No description provided"
        }
    else:
        # Scrape supported sites
        scraper = JobScraper(headless=False)
        job_data = scraper.scrape(url)

    print("\n" + "=" * 60)
    print("📋 EXTRACTED JOB DETAILS")
    print("=" * 60)
    for key, value in job_data.items():
        print(f"{key.title().replace('_', ' '):<12} : {value}")
    print("=" * 60)

    # Resume input
    print("\n📄 Resume Analysis")
    print("-" * 40)
    resume_path = input("Enter path to your resume (PDF or DOCX): ").strip()

    if not os.path.exists(resume_path):
        print("⚠️  File not found. Skipping analysis.")
        resume_text = ""
    else:
        resume_text = read_resume(resume_path)
        if not resume_text:
            print("⚠️  Could not extract text from resume.")
            resume_text = ""

    # Keyword suggestions
    suggestions, certs = suggest_resume_keywords(job_data["title"], job_data["description"])

    print("\n🎯 SUGGESTED RESUME KEYWORDS")
    print("-" * 60)
    if certs:
        print(f"🎖️  Add Certifications: {', '.join(certs)}")
    any_suggested = False
    for category, terms in suggestions.items():
        if terms:
            print(f"{category:<18}: {', '.join(terms[:8])}{'...' if len(terms) > 8 else ''}")
            any_suggested = True
    if not any_suggested and not certs:
        print("No strong keyword matches found.")

    # Match score
    if resume_text:
        print("\n📊 RESUME MATCH ANALYSIS")
        print("-" * 60)
        score, matched, missing = calculate_match_score(resume_text, job_data["description"])
        print(f"🎯 Match Score: {score:.1f}%")
        print(f"✅ Found: {len(matched)} keywords")
        print(f"❌ Missing: {len(missing)} keywords (e.g., {', '.join(list(set(missing))[:5])}...)")

        if score < 60:
            print("💡 Tip: Your resume is missing key technical terms. Add more role-specific skills.")
        elif score < 80:
            print("💡 Tip: Tailor your bullet points to match job responsibilities.")
        else:
            print("✅ Excellent match! Strong candidate for this role.")

        if missing:
            top_missing = [w.title() for w in missing[:3] if len(w) > 4]
            if top_missing:
                print(f"\n💡 Add to Resume: {', '.join(top_missing)}")
    else:
        score, matched, missing = 0, [], []
        print("⚠️  Could not analyze resume. Skipping match score.")

    # ✅ Always save recommendations if job data exists
    save_recommendations(job_data, suggestions, certs, missing, resume_path)
    # Export job data
    if "linkedin.com" not in url.lower() and "tecoloco.com" not in url.lower():
        scraper.export_json()
        scraper.export_csv()
    else:
        with open("job_data.json", "w", encoding="utf-8") as f:
            json.dump(job_data, f, indent=4, ensure_ascii=False)
        file_exists = os.path.isfile("job_data.csv")
        with open("job_data.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=job_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(job_data)
        print("📁 Exported to job_data.json and job_data.csv")

    # ✅ Save application only if resume was analyzed
    if resume_text and "Failed to scrape" not in job_data["title"]:
        follow_up = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        app_data = {
            "timestamp": datetime.now().isoformat(),
            "job_title": job_data["title"],
            "company": job_data["company"],
            "job_url": url,
            "ats_score": round(score, 1),
            "missing_keywords": list(set(missing))[:50],
            "resume_version": os.path.basename(resume_path),
            "status": "applied",
            "follow_up_date": follow_up
        }
        save_application(app_data)

    print("=" * 60)
    print("✅ Job analysis complete! Update your resume with the keywords above.")
    print("=" * 60)

    return job_data


if __name__ == "__main__":
    url = input("🌐 Enter job URL: ").strip()
    if not url.startswith("http"):
        print("❌ Invalid URL. Please use http:// or https://")
    else:
        try:
            result = optimize_resume_for_job(url)
        except KeyboardInterrupt:
            print("\n👋 Optimization stopped by user.")
        except Exception as e:
            print(f"💥 Unexpected error: {e}")