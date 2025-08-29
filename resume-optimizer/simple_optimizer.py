import PyPDF2
import re
from collections import Counter

class QuickResumeHelper:
    def __init__(self, resume_path="VICTOR MARTINEZ - Telecommunications and Cybersecurity Engineer Resume.pdf"):
        self.resume_path = resume_path
        self.resume_text = self.extract_resume_text()
    
    def extract_resume_text(self):
        """Extract text from your PDF resume"""
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
    
    def extract_keywords_from_job_file(self, job_file_path):
        """Extract keywords from a job description file"""
        try:
            with open(job_file_path, 'r', encoding='utf-8') as file:
                job_text = file.read()
            return self.extract_keywords_from_text(job_text)
        except Exception as e:
            print(f"Error reading job file: {e}")
            return []
    
    def extract_keywords_from_text(self, text):
        """Extract important keywords from job description"""
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
            'we', 'they', 'not', 'no', 'from', 'up', 'out', 'about', 'into', 'over',
            'after', 'before', 'during', 'under', 'above', 'below', 'between', 'among',
            'an', 'as', 'been', 'being', 'has', 'had', 'have', 'did', 'does', 'done'
        }
        
        # Extract words (3+ characters)
        words = re.findall(r'\b[A-Za-z]{3,25}\b', text.lower())
        
        # Filter out stop words and get most common words
        filtered_words = [word for word in words if word not in stop_words]
        word_freq = Counter(filtered_words)
        
        # Return top 30 most frequent words (more comprehensive for this detailed job)
        return [word for word, freq in word_freq.most_common(30)]
    
    def analyze_job_match(self, job_keywords):
        """Analyze how well your resume matches job keywords"""
        if not job_keywords:
            return {"error": "No keywords found"}
        
        # Check which keywords are in your resume
        present_keywords = []
        missing_keywords = []
        
        for keyword in job_keywords:
            # Check for exact match or partial match in your resume text
            if keyword.lower() in self.resume_text:
                present_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate compatibility score
        compatibility = (len(present_keywords) / len(job_keywords)) * 100 if job_keywords else 0
        
        return {
            'compatibility_score': round(compatibility, 1),
            'present_keywords': present_keywords[:15],  # Show more present keywords
            'missing_keywords': missing_keywords[:15],  # Show more missing keywords
            'total_found': len(present_keywords),
            'total_analyzed': len(job_keywords)
        }
    
    def generate_suggestions(self, job_keywords):
        """Generate actionable suggestions"""
        analysis = self.analyze_job_match(job_keywords)
        
        if "error" in analysis:
            return analysis
        
        suggestions = []
        score = analysis['compatibility_score']
        
        # Score-based feedback
        if score < 50:
            suggestions.append("🔴 MAJOR IMPROVEMENT NEEDED - Consider rewriting key sections")
        elif score < 75:
            suggestions.append("🟡 GOOD - Add missing keywords to improve ATS score")
        else:
            suggestions.append("🟢 EXCELLENT MATCH - Your resume is well-optimized!")
        
        # Specific suggestions based on missing keywords
        if analysis['missing_keywords']:
            top_missing = analysis['missing_keywords'][:8]
            suggestions.append(f"ADD THESE KEYWORDS: {', '.join(top_missing)}")
        
        # Industry-specific suggestions
        security_keywords = [k for k in analysis['missing_keywords'] if any(sec in k.lower() for sec in ['security', 'siem', 'incident', 'threat', 'vulnerability', 'detection'])]
        if security_keywords:
            suggestions.append(f"SECURITY FOCUS: Add '{', '.join(security_keywords[:5])}'")
        
        return {
            'ats_score': analysis['compatibility_score'],
            'suggestions': suggestions,
            'missing_keywords': analysis['missing_keywords'],
            'analysis': analysis
        }

# Test with your resume and the SOC analyst job description
if __name__ == "__main__":
    # Initialize the optimizer
    optimizer = QuickResumeHelper()
    
    # Test with the SOC analyst job description file
    job_keywords = optimizer.extract_keywords_from_job_file("cybersecurity_job.txt")
    
    if job_keywords:
        print("Extracted job keywords:", job_keywords[:10])  # Show first 10 keywords
        
        # Generate suggestions
        result = optimizer.generate_suggestions(job_keywords)
        
        # Display results
        print("\n" + "=" * 60)
        print("RESUME OPTIMIZATION REPORT - SOC CYBERSECURITY ANALYST")
        print("=" * 60)
        print(f"ATS Compatibility Score: {result['ats_score']}%")
        print(f"Keywords Found: {result['analysis']['total_found']}/{result['analysis']['total_analyzed']}")
        print("\nSUGGESTIONS:")
        for suggestion in result['suggestions']:
            print(f"  • {suggestion}")
        
        if result['missing_keywords']:
            print(f"\nMISSING KEYWORDS TO ADD:")
            for i, keyword in enumerate(result['missing_keywords'][:12], 1):
                print(f"  {i:2d}. {keyword}")
    else:
        print("Could not extract keywords from job description file")