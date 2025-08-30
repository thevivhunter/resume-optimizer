# automated_resume_optimizer.py
import PyPDF2
import re
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import Counter
import json
import os
from datetime import datetime

class AutomatedResumeOptimizer:
    def __init__(self, resume_path):
        self.resume_path = resume_path
        self.resume_text = self.extract_resume_text()
        self.critical_soc_keywords = [
            'threat', 'detection', 'incident', 'response', 'siem', 'triage', 
            'analyst', 'investigation', 'malware', 'vulnerability', 'monitoring',
            'security', 'log', 'alert', 'forensics', 'hunt', 'intelligence'
        ]
    
    def extract_resume_text(self):
        """Extract text from PDF resume"""
        try:
            with open(self.resume_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.lower()
        except Exception as e:
            print(f"Error reading resume: {e}")
            return ""
    
    # Update in automated_resume_optimizer.py
    def extract_job_description_from_url(self, url):
        """Extract job description from tecoloco.com.hn and other job boards"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Specific selectors for tecoloco.com.hn
            selectors = [
                '.job-description',  # Standard job description class
                '#jobDescriptionText',  # Common ID for job descriptions
                '.job-details-content',
                '.description',  # General description class
                '.content',  # Fallback
                'article',  # Common tag for job postings
                '.container',  # Container that might hold job content
                '.row',  # Bootstrap row that might contain job content
                '[class*="job"]',  # Any class containing "job"
                '[class*="description"]'  # Any class containing "description"
            ]
            
            job_text = ""
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    # Extract text from all matching elements
                    text_parts = []
                    for element in elements:
                        # Remove common non-content elements
                        for exclude in element(["button", "nav", "footer", "header", "aside"]):
                            exclude.decompose()
                        
                        text = element.get_text().strip()
                        if len(text) > 50:  # Only include substantial text blocks
                            text_parts.append(text)
                    
                    job_text = ' '.join(text_parts)
                    # Clean up the text
                    job_text = re.sub(r'\s+', ' ', job_text)
                    
                    # Check if we have meaningful content
                    if len(job_text) > 200:
                        # Remove common site navigation text
                        job_text = re.sub(r'Compartir|Comparte esta vacante|Vacantes relacionadas|Síguenos en|Política de privacidad|Condiciones de uso|Aviso de privacidad', '', job_text)
                        break
            
            if job_text and len(job_text) > 200:
                return job_text
            else:
                return "Could not extract job description from the provided URL. The website structure may require specific parsing."
                
        except requests.exceptions.RequestException as e:
            return f"Error fetching job description: {e}"
        except Exception as e:
            return f"Error parsing job description: {e}"
    
    def extract_keywords_from_text(self, text):
        """Extract important keywords from text"""
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
            'we', 'they', 'not', 'no', 'from', 'up', 'out', 'about', 'into', 'over',
            'after', 'before', 'during', 'under', 'above', 'below', 'between', 'among'
        }
        
        words = re.findall(r'\b[A-Za-z]{3,20}\b', text.lower())
        filtered_words = [word for word in words if word not in stop_words]
        word_freq = Counter(filtered_words)
        return [word for word, freq in word_freq.most_common(25)]
    
    def analyze_job_match(self, job_keywords):
        """Analyze how well resume matches job keywords"""
        if not job_keywords:
            return {"error": "No keywords found"}
        
        present_keywords = []
        missing_keywords = []
        
        for keyword in job_keywords:
            if keyword.lower() in self.resume_text:
                present_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        compatibility = (len(present_keywords) / len(job_keywords)) * 100 if job_keywords else 0
        
        return {
            'compatibility_score': round(compatibility, 1),
            'present_keywords': present_keywords[:10],
            'missing_keywords': missing_keywords[:10],
            'total_found': len(present_keywords),
            'total_analyzed': len(job_keywords)
        }
    
    def analyze_soc_specific_match(self):
        """Analyze against SOC analyst requirements"""
        found_keywords = []
        missing_keywords = []
        
        for keyword in self.critical_soc_keywords:
            if keyword in self.resume_text:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        score = (len(found_keywords) / len(self.critical_soc_keywords)) * 100
        
        return {
            'score': round(score, 1),
            'found': found_keywords,
            'missing': missing_keywords,
            'total_found': len(found_keywords),
            'total_possible': len(self.critical_soc_keywords)
        }
    
    def generate_actionable_suggestions(self, job_description=None):
        """Generate specific suggestions for improvement"""
        if job_description:
            job_keywords = self.extract_keywords_from_text(job_description)
            analysis = self.analyze_job_match(job_keywords)
        else:
            analysis = self.analyze_soc_specific_match()
        
        suggestions = []
        
        # Score feedback
        score = analysis.get('score', analysis.get('compatibility_score', 0))
        if score < 40:
            suggestions.append("🔴 URGENT: Major keyword gap for cybersecurity positions")
        elif score < 60:
            suggestions.append("🟡 NEEDS WORK: Add cybersecurity keywords to key sections")
        else:
            suggestions.append("🟢 GOOD: Strong cybersecurity keyword presence")
        
        # Specific suggestions based on missing keywords
        missing = analysis.get('missing_keywords', analysis.get('missing', []))
        
        if 'threat' in missing:
            suggestions.append("Add 'threat detection' to your monitoring experience")
        
        if 'incident' in missing or 'response' in missing:
            suggestions.append("Reframe 'ticket resolution' as 'incident response' - you have the 25% improvement metric!")
        
        if 'triage' in missing:
            suggestions.append("Add 'alert triage' to your customer support roles")
        
        if 'investigation' in missing:
            suggestions.append("Use 'security investigations' instead of general troubleshooting")
        
        return {
            'ats_score': score,
            'suggestions': suggestions,
            'missing_keywords': missing[:10],
            'analysis': analysis
        }
    
    def send_optimization_report(self, job_url, suggestions, email_config):
        """Send optimization report via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = email_config['recipient_email']
            msg['Subject'] = f"Resume Optimization Report - ATS Score: {suggestions['ats_score']}%"
            
            body = f"""
            Resume Optimization Report
            ==========================
            
            Job URL: {job_url}
            ATS Compatibility Score: {suggestions['ats_score']}%
            
            SUGGESTIONS:
            {chr(10).join([f'  • {s}' for s in suggestions['suggestions']])}
            
            MISSING KEYWORDS TO ADD:
            {chr(10).join([f'  • {keyword}' for keyword in suggestions['missing_keywords']])}
            
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email_config['sender_email'], email_config['app_password'])
            text = msg.as_string()
            server.sendmail(email_config['sender_email'], email_config['recipient_email'], text)
            server.quit()
            
            print("Optimization report sent successfully!")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def save_optimization_report(self, job_url, suggestions, filename=None):
        """Save optimization report to file with proper encoding"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"optimization_report_{timestamp}.txt"
        
        try:
            # Use utf-8 encoding to handle special characters
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Resume Optimization Report\n")
                f.write(f"==========================\n\n")
                f.write(f"Job URL: {job_url}\n")
                f.write(f"ATS Compatibility Score: {suggestions['ats_score']}%\n\n")
                
                f.write("SUGGESTIONS:\n")
                # Replace emojis with plain text equivalents
                for suggestion in suggestions['suggestions']:
                    # Remove or replace emojis
                    clean_suggestion = suggestion.replace("🔴", "[HIGH PRIORITY]")
                    clean_suggestion = clean_suggestion.replace("🟡", "[MEDIUM PRIORITY]")
                    clean_suggestion = clean_suggestion.replace("🟢", "[GOOD]")
                    clean_suggestion = clean_suggestion.replace("💡", "[TIP]")
                    clean_suggestion = clean_suggestion.replace("📌", "[NOTE]")
                    clean_suggestion = clean_suggestion.replace("🎯", "[RECOMMENDATION]")
                    f.write(f"  • {clean_suggestion}\n")
                
                f.write(f"\nMISSING KEYWORDS TO ADD:\n")
                for keyword in suggestions['missing_keywords']:
                    f.write(f"  • {keyword}\n")
                
                f.write(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"Optimization report saved to {filename}")
            return filename
        except Exception as e:
            print(f"Error saving report: {e}")
            return None

# Test the automated optimizer
if __name__ == "__main__":
    # Initialize with your optimized resume
    optimizer = AutomatedResumeOptimizer("CV_Victor_Martinez.pdf")
    
    # Test with SOC analyst job description
    soc_job_description = """
    The Cybersecurity Analyst is responsible for identifying, investigating, and remediating threats – both internal and external. The Cybersecurity Analyst is expected to understand threats, attacks, and malware to develop enterprise detections and protections. Analysts must also perform security control maintenance in the form of detection tuning, control policy updates, and automations. Reporting of metrics and summaries of weekly investigations/ ticket tracking is required. This role is leveraged by senior level analysts for more complex investigations and duties.

    The SOC Cybersecurity Analyst will be responsible for evaluating the effectiveness and improving the following technology domains in place:

        Security Incident and Event Management (SIEM) review.
        Alert triage.
        Data Protection Domain: includes DLP, URL Content filtering, CASB.
        Endpoint Threat Detection: includes EDR capabilities, traditional antivirus, asset management, and familiarity with baseline and configuration management tools.
        Next Generation Firewalls and/or IDS/IPS.
        Threat Hunting & Threat Intelligence.
        Threat Intelligence Platforms (TIP).
        Malware sandbox technologies & interpreting results.
        Incident Response tools, process, and capabilities.
        Splunk Enterprise Security experience desired.
        Perform other duties as assigned.

    Experience Needed

        Bachelor's Degree preferred
        0-3 years working within Cybersecurity field
        Proven technical proficiency in the form of independent research and projects.
        Proficiency with the identification, triage, and analysis of security events using a SIEM.
        Demonstrated understanding of attacker methodology.
        Experience with or knowledge of vulnerability and configuration management.
    """
    
    # Generate suggestions
    result = optimizer.generate_actionable_suggestions(soc_job_description)
    
    # Display results
    print("=" * 60)
    print("AUTOMATED RESUME OPTIMIZER - SOC ANALYST FOCUS")
    print("=" * 60)
    print(f"ATS Compatibility Score: {result['ats_score']}%")
    print("\nACTIONABLE SUGGESTIONS:")
    for suggestion in result['suggestions']:
        print(f"  • {suggestion}")
    
    if result['missing_keywords']:
        print(f"\nMISSING KEYWORDS TO ADD:")
        for i, keyword in enumerate(result['missing_keywords'][:8], 1):
            print(f"  {i}. {keyword}")
    
    # Save report
    optimizer.save_optimization_report("SOC Analyst Position", result)