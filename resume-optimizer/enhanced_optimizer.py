# enhanced_optimizer.py
import PyPDF2
import re
from collections import Counter

class ResumeOptimizer:
    def __init__(self, resume_path):
        self.resume_path = resume_path
        self.resume_text = self.extract_text()
    
    def extract_text(self):
        """Extract text from PDF resume"""
        try:
            with open(self.resume_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.lower()
        except Exception as e:
            print(f"Error: {e}")
            return ""
    
    def analyze_soc_job_match(self):
        """Analyze against SOC analyst requirements"""
        # Critical keywords for SOC analyst positions
        critical_keywords = [
            'threat', 'detection', 'incident', 'response', 'siem', 'triage', 
            'analyst', 'investigation', 'malware', 'vulnerability', 'monitoring',
            'security', 'log', 'alert', 'forensics', 'hunt', 'intelligence'
        ]
        
        found_keywords = []
        missing_keywords = []
        
        for keyword in critical_keywords:
            if keyword in self.resume_text:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        score = (len(found_keywords) / len(critical_keywords)) * 100
        
        return {
            'score': round(score, 1),
            'found': found_keywords,
            'missing': missing_keywords,
            'total_found': len(found_keywords),
            'total_possible': len(critical_keywords)
        }
    
    def generate_actionable_suggestions(self):
        """Generate specific suggestions for improvement"""
        analysis = self.analyze_soc_job_match()
        
        suggestions = []
        
        # Score feedback
        if analysis['score'] < 40:
            suggestions.append("🔴 URGENT: Major keyword gap for cybersecurity positions")
        elif analysis['score'] < 60:
            suggestions.append("🟡 NEEDS WORK: Add cybersecurity keywords to key sections")
        else:
            suggestions.append("🟢 GOOD: Strong cybersecurity keyword presence")
        
        # Specific suggestions based on missing keywords
        if 'threat' in analysis['missing']:
            suggestions.append("Add 'threat detection' to your monitoring experience")
        
        if 'incident' in analysis['missing'] or 'response' in analysis['missing']:
            suggestions.append("Reframe 'ticket resolution' as 'incident response' - you have the 25% improvement metric!")
        
        if 'triage' in analysis['missing']:
            suggestions.append("Add 'alert triage' to your customer support roles")
        
        if 'investigation' in analysis['missing']:
            suggestions.append("Use 'security investigations' instead of general troubleshooting")
        
        return {
            'ats_score': analysis['score'],
            'suggestions': suggestions,
            'missing_keywords': analysis['missing'][:10]
        }

# Test with your resume
if __name__ == "__main__":
    optimizer = ResumeOptimizer("CV_Victor_Martinez.pdf" )  
    result = optimizer.generate_actionable_suggestions()
    
    print("=" * 50)
    print("RESUME OPTIMIZER - SOC ANALYST FOCUS")
    print("=" * 50)
    print(f"ATS Compatibility Score: {result['ats_score']}%")
    print("\nACTIONABLE SUGGESTIONS:")
    for suggestion in result['suggestions']:
        print(f"  • {suggestion}")
    
    print(f"\nMISSING KEYWORDS TO ADD:")
    for keyword in result['missing_keywords']:
        print(f"  • {keyword}")