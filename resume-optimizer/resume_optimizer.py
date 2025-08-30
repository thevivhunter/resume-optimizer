# resume_optimizer.py
from job_scraper import JobScraper
import spacy
import re

nlp = spacy.load("en_core_web_sm")

# Skill keywords database
SKILL_KEYWORDS = {
    "technical": [
        "python", "java", "aws", "docker", "kubernetes", "git", "ci/cd", "sql", "linux",
        "networking", "firewall", "cisco", "vpn", "vlan", "routing", "switching",
        "active directory", "powershell", "scripting", "cybersecurity", "it support",
        "ccna", "ccnp", "compliance", "migration", "infrastructure", "monitoring"
    ],
    "soft": [
        "leadership", "communication", "teamwork", "problem-solving", "project management",
        "time management", "collaboration", "adaptability", "analytical skills"
    ],
    "roles": [
        "supervisor", "manager", "engineer", "developer", "analyst", "administrator",
        "consultant", "architect", "coordinator", "director", "specialist"
    ]
}

# Blacklist generic or weak words
BLACKLIST = {
    "ability", "background", "bachelor", "degree", "experience", "role", "job",
    "team", "work", "skills", "position", "candidate", "individual", "excellent",
    "strong", "good", "help", "support", "make", "use", "perform", "carry out"
}

def extract_keywords_from_text(text):
    doc = nlp(text.lower())
    tokens = [
        token.lemma_ for token in doc
        if not token.is_stop and not token.is_punct and len(token.lemma_) > 2
    ]
    return set(tokens)

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
        elif word_upper := word.upper() in ["CCNA", "CCNP", "CISSP", "AWS", "AZURE", "GCP", "ITIL", "PMP"]:
            certifications.append(word_upper)
        elif word_lower not in BLACKLIST and re.match(r"^[a-z]{3,}$", word_lower):
            suggestions["Other Keywords"].append(word.title())

    # Deduplicate and sort
    for key in suggestions:
        suggestions[key] = sorted(list(set(suggestions[key])))

    return suggestions, certifications

def optimize_resume_for_job(url):
    print("🔍 Resume Optimizer - Smart Job Keyword Analyzer")
    print("💡 Paste any job URL from Workable, Greenhouse, Lever, or LinkedIn\n")

    scraper = JobScraper(headless=False)  # Set to True later
    job_data = scraper.scrape(url)

    print("\n" + "="*60)
    print("📋 EXTRACTED JOB DETAILS")
    print("="*60)
    for key, value in job_data.items():
        print(f"{key.title().replace('_', ' '):<12} : {value}")
    print("="*60)

    print("\n🎯 SUGGESTED RESUME KEYWORDS")
    print("-"*60)

    suggestions, certs = suggest_resume_keywords(job_data["title"], job_data["description"])

    # Show certifications first
    if certs:
        print(f"🎖️  Add Certifications: {', '.join(certs)}")

    any_suggested = False
    for category, terms in suggestions.items():
        if terms:
            print(f"{category:<18}: {', '.join(terms[:8])}{'...' if len(terms) > 8 else ''}")
            any_suggested = True

    if not any_suggested and not certs:
        print("No strong keyword matches found. Try another job posting.")

    print("\n" + "-"*60)
    scraper.export_json()
    scraper.export_csv()
    print("="*60)
    print("✅ Job analysis complete! Update your resume with the keywords above.")
    print("="*60)

    return job_data


if __name__ == "__main__":
    url = input("🌐 Enter job URL: ").strip()
    if not url.startswith("http"):
        print("❌ Invalid URL. Please use a valid link starting with http:// or https://")
    else:
        try:
            result = optimize_resume_for_job(url)
        except KeyboardInterrupt:
            print("\n👋 Optimization stopped by user.")
        except Exception as e:
            print(f"💥 Unexpected error: {e}")