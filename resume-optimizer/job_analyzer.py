# job_analyzer.py
import re
from typing import Dict, List, Set
from collections import Counter

class JobAnalyzer:
    def __init__(self):
        # Cybersecurity-specific keyword categories
        self.keyword_categories = {
            'core_skills': ['siem', 'incident', 'response', 'threat', 'detection', 'monitoring', 'vulnerability'],
            'tools': ['splunk', 'arcsight', 'qradar', 'sentinelone', 'defender', 'firewall', 'ids', 'ips'],
            'experience': ['analyst', 'soc', 'security operations', 'forensics', 'malware', 'triage'],
            'certifications': ['cissp', 'cisa', 'cism', 'security+', 'ceh', 'gcih', 'gcia', 'gcih'],
            'responsibilities': ['investigation', 'analysis', 'reporting', 'hunting', 'intelligence']
        }
        
        # Experience level indicators
        self.experience_levels = {
            'entry': ['0-2 years', 'entry', 'junior', 'associate'],
            'mid': ['3-5 years', 'mid-level', 'intermediate'],
            'senior': ['5+ years', 'senior', 'lead', 'principal']
        }
    
    def analyze_job_description(self, job_text: str) -> Dict:
        """Comprehensive analysis of job description"""
        job_text_lower = job_text.lower()
        
        # Extract keywords by category
        categorized_keywords = {}
        total_keywords = []
        
        for category, keywords in self.keyword_categories.items():
            found_keywords = [kw for kw in keywords if kw in job_text_lower]
            categorized_keywords[category] = found_keywords
            total_keywords.extend(found_keywords)
        
        # Analyze experience requirements
        experience_level = self._determine_experience_level(job_text_lower)
        
        # Extract responsibilities
        responsibilities = self._extract_responsibilities(job_text)
        
        # Calculate keyword density and importance
        keyword_analysis = self._analyze_keyword_importance(job_text_lower, total_keywords)
        
        return {
            'categorized_keywords': categorized_keywords,
            'total_keywords': list(set(total_keywords)),
            'experience_level': experience_level,
            'responsibilities': responsibilities,
            'keyword_analysis': keyword_analysis,
            'job_text_length': len(job_text)
        }
    
    def _determine_experience_level(self, text: str) -> str:
        """Determine required experience level"""
        for level, indicators in self.experience_levels.items():
            if any(indicator in text for indicator in indicators):
                return level
        return 'mid'  # Default assumption
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract responsibility statements"""
        # Look for bullet points or statements starting with action verbs
        sentences = re.split(r'[.!?]+', text)
        responsibilities = []
        
        action_verbs = ['analyze', 'monitor', 'detect', 'respond', 'investigate', 'implement', 'develop', 'manage']
        
        for sentence in sentences:
            sentence_clean = sentence.strip().lower()
            if any(verb in sentence_clean for verb in action_verbs) and len(sentence_clean) > 10:
                responsibilities.append(sentence_clean)
        
        return responsibilities[:10]  # Return top 10
    
    def _analyze_keyword_importance(self, text: str, keywords: List[str]) -> Dict:
        """Analyze importance of keywords based on context"""
        # Simple frequency analysis for now
        word_freq = Counter(re.findall(r'\b\w+\b', text))
        keyword_scores = {}
        
        for keyword in keywords:
            keyword_scores[keyword] = word_freq.get(keyword, 0)
        
        return keyword_scores

# Enhanced resume analyzer
class EnhancedResumeAnalyzer:
    def __init__(self, resume_text: str):
        self.resume_text = resume_text.lower()
        self.resume_lines = resume_text.split('\n')
    
    def extract_sections(self) -> Dict[str, str]:
        """Extract resume sections"""
        sections = {
            'summary': '',
            'experience': '',
            'skills': '',
            'education': ''
        }
        
        current_section = None
        section_content = []
        
        # Simple section detection based on common headers
        section_headers = {
            'summary': ['summary', 'professional summary', 'objective'],
            'experience': ['experience', 'work experience', 'employment'],
            'skills': ['skills', 'core skills', 'technical skills'],
            'education': ['education', 'academic background']
        }
        
        for line in self.resume_lines:
            line_lower = line.lower().strip()
            
            # Check if this line is a section header
            found_section = False
            for section_name, headers in section_headers.items():
                if any(header in line_lower for header in headers):
                    # Save previous section
                    if current_section and section_content:
                        sections[current_section] = '\n'.join(section_content)
                    
                    # Start new section
                    current_section = section_name
                    section_content = []
                    found_section = True
                    break
            
            if not found_section and current_section:
                section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)
        
        return sections
    
    def analyze_competency_gaps(self, job_analysis: Dict) -> Dict:
        """Analyze gaps between job requirements and resume competencies"""
        # Extract resume keywords
        resume_keywords = self._extract_resume_keywords()
        
        # Compare with job requirements
        job_keywords = job_analysis['total_keywords']
        missing_keywords = [kw for kw in job_keywords if kw not in resume_keywords]
        matching_keywords = [kw for kw in job_keywords if kw in resume_keywords]
        
        # Categorize missing keywords by importance
        categorized_gaps = {}
        for category, keywords in job_analysis['categorized_keywords'].items():
            gaps = [kw for kw in keywords if kw not in resume_keywords]
            if gaps:
                categorized_gaps[category] = gaps
        
        return {
            'matching_keywords': matching_keywords,
            'missing_keywords': missing_keywords,
            'categorized_gaps': categorized_gaps,
            'match_percentage': len(matching_keywords) / len(job_keywords) * 100 if job_keywords else 0
        }
    
    def _extract_resume_keywords(self) -> Set[str]:
        """Extract keywords from resume"""
        # Simple keyword extraction - can be enhanced
        words = re.findall(r'\b\w+\b', self.resume_text)
        return set(word.lower() for word in words if len(word) > 2)

# Integration with existing optimizer
class IntegratedOptimizer:
    def __init__(self, resume_path: str):
        from automated_resume_optimizer import AutomatedResumeOptimizer
        self.base_optimizer = AutomatedResumeOptimizer(resume_path)
        self.job_analyzer = JobAnalyzer()
    
    def comprehensive_analysis(self, job_description: str) -> Dict:
        """Comprehensive analysis combining all features"""
        # Basic analysis
        basic_suggestions = self.base_optimizer.generate_actionable_suggestions(job_description)
        
        # Enhanced analysis
        job_analysis = self.job_analyzer.analyze_job_description(job_description)
        resume_analyzer = EnhancedResumeAnalyzer(self.base_optimizer.resume_text)
        competency_gaps = resume_analyzer.analyze_competency_gaps(job_analysis)
        
        # Combine results
        return {
            'basic_analysis': basic_suggestions,
            'job_analysis': job_analysis,
            'competency_gaps': competency_gaps,
            'enhanced_recommendations': self._generate_enhanced_recommendations(competency_gaps, job_analysis)
        }
    
    def _generate_enhanced_recommendations(self, gaps: Dict, job_analysis: Dict) -> List[str]:
        """Generate enhanced recommendations based on detailed analysis"""
        recommendations = []
        
        # Experience level recommendations
        if job_analysis['experience_level'] == 'senior':
            recommendations.append("💼 Senior-level position detected - emphasize leadership experience")
        
        # Skill gap recommendations
        if gaps['categorized_gaps'].get('tools'):
            tools_needed = ', '.join(gaps['categorized_gaps']['tools'])
            recommendations.append(f"🛠️ Add experience with these tools: {tools_needed}")
        
        if gaps['categorized_gaps'].get('certifications'):
            certs_needed = ', '.join(gaps['categorized_gaps']['certifications'])
            recommendations.append(f"📜 Consider highlighting or obtaining: {certs_needed}")
        
        # Core skill recommendations
        if gaps['categorized_gaps'].get('core_skills'):
            core_skills = ', '.join(gaps['categorized_gaps']['core_skills'])
            recommendations.append(f"🎯 Add these core skills to your experience: {core_skills}")
        
        return recommendations

# Example usage
if __name__ == "__main__":
    # Test with your optimized resume
    optimizer = IntegratedOptimizer("CV_Victor_Martinez.pdf")
    
    # Sample SOC analyst job description
    soc_job = """
    Cybersecurity Analyst - SOC Operations
    
    System Administrator with excellent technical support and troubleshooting skills. This remote role involves server and computer maintenance, cloud backup administration, and end-user support.

    As Part Of The Team, You Will

    Configure and maintain servers and operating systems. 
    Install software and ensure network connectivity. 
    Administer and monitor cloud backup systems. 
    Provide technical support to colleagues and clients, resolving issues with efficiency and professionalism. 

    This role is ideal for a tech-savvy professional with strong problem-solving abilities, solid communication skills in English, and a proactive approach to IT challenges.

    Requirements

    C1 level of English is a must (spoken and written). 
    +3 years of experience in the same role.
    Excellent verbal and written communication skills. 
    Advanced PC knowledge (ability to assemble and upgrade computers). 
    Extensive experience with Windows 10/11, Server 2016/22. 
    Ability to set up and maintain domain controllers. 
    Strong experience in networking and troubleshooting connectivity issues. 
    Knowledge of configuring firewalls, opening ports, and setting up high availability redundancy for dual ISPs. 
    Experience setting up printers, scanners, and fax machines. 
    Strong troubleshooting and time management skills with the ability to meet deadlines. 

    """
    
    # Comprehensive analysis
    results = optimizer.comprehensive_analysis(soc_job)
    
    print("=== COMPREHENSIVE RESUME ANALYSIS ===")
    print(f"Match Percentage: {results['competency_gaps']['match_percentage']:.1f}%")
    print(f"Missing Keywords: {', '.join(results['competency_gaps']['missing_keywords'])}")
    print("\nEnhanced Recommendations:")
    for rec in results['enhanced_recommendations']:
        print(f"  • {rec}")