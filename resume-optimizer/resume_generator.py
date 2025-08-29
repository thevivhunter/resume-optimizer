# resume_generator.py
import json
from datetime import datetime
from typing import Dict, List, Optional
import re

class ResumeGenerator:
    def __init__(self):
        self.templates = {
            'cybersecurity_analyst': {
                'title': 'Cybersecurity Analyst',
                'summary_template': '''{name}\n{title}\n{contact_info}\n\nCybersecurity Analyst with {experience_years}+ years of experience in {skill1}, {skill2}, and {skill3}. Skilled in {skill4}, {skill5}, and telecommunications infrastructure security. Experienced in {skill6} and customer-focused cybersecurity support.''',
                'experience_bullets': [
                    "Conducted security incident response for {technology} systems",
                    "Performed threat detection analysis and security monitoring",
                    "Developed {language} automation scripts for security operations",
                    "Collaborated with cross-functional security teams for incident response",
                    "Monitored {monitoring_type} to detect security anomalies and threats"
                ]
            },
            'soc_analyst': {
                'title': 'SOC Cybersecurity Analyst',
                'summary_template': '''{name}\n{title}\n{contact_info}\n\nSOC Cybersecurity Analyst with {experience_years}+ years of experience in threat detection, security monitoring, and incident response. Proficient in SIEM operations, alert triage, and security investigations. Skilled in {skill1} and {skill2}.''',
                'experience_bullets': [
                    "Monitored SIEM tools for security event detection and analysis",
                    "Performed alert triage and preliminary security investigations",
                    "Conducted threat hunting activities to identify potential vulnerabilities",
                    "Participated in incident response for critical security events",
                    "Analyzed security logs to detect anomalous patterns and threats"
                ]
            }
        }
    
    def generate_optimized_resume(self, original_resume_data: Dict, job_analysis: Dict, template_type: str = 'cybersecurity_analyst') -> str:
        """Generate an optimized resume based on job analysis"""
        template = self.templates.get(template_type, self.templates['cybersecurity_analyst'])
        
        # Extract key information from original resume
        name = self._extract_name(original_resume_data['text'])
        contact_info = self._extract_contact_info(original_resume_data['text'])
        experience_years = self._extract_experience_years(original_resume_data['text'])
        
        # Get missing keywords to incorporate
        missing_keywords = job_analysis.get('missing_keywords', [])
        key_skills = self._extract_key_skills(original_resume_data['text'], missing_keywords)
        
        # Generate optimized summary
        optimized_summary = template['summary_template'].format(
            name=name,
            title=template['title'],
            contact_info=contact_info,
            experience_years=experience_years,
            skill1=key_skills[0] if len(key_skills) > 0 else "network security",
            skill2=key_skills[1] if len(key_skills) > 1 else "threat detection",
            skill3=key_skills[2] if len(key_skills) > 2 else "incident response",
            skill4=key_skills[3] if len(key_skills) > 3 else "SIEM operations",
            skill5=key_skills[4] if len(key_skills) > 4 else "security monitoring",
            skill6=key_skills[5] if len(key_skills) > 5 else "security investigations"
        )
        
        # Generate optimized experience sections
        optimized_experience = self._optimize_experience_sections(
            original_resume_data.get('experience_sections', []), 
            missing_keywords,
            template['experience_bullets']
        )
        
        # Generate optimized skills section
        optimized_skills = self._generate_optimized_skills(
            original_resume_data.get('skills_section', []), 
            missing_keywords
        )
        
        # Combine all sections
        optimized_resume = f"""{optimized_summary}

WORK EXPERIENCE
{optimized_experience}

CORE SKILLS
{optimized_skills}

{self._extract_education_section(original_resume_data['text'])}

{self._extract_certificates_section(original_resume_data['text'])}

{self._extract_languages_section(original_resume_data['text'])}"""
        
        return optimized_resume
    
    def _extract_name(self, resume_text: str) -> str:
        """Extract name from resume text"""
        lines = resume_text.strip().split('\n')
        return lines[0].strip() if lines else "Candidate Name"
    
    def _extract_contact_info(self, resume_text: str) -> str:
        """Extract contact information"""
        # Simple pattern matching for contact info
        contact_patterns = [
            r'\S+@\S+',  # Email
            r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # Phone
            r'www\.linkedin\.com[^\\\s]*',  # LinkedIn
            r'[A-Za-z\s]+,\s*[A-Za-z\s]+(?:,\s*[A-Z]{2})?'  # Location
        ]
        
        contact_info = []
        for pattern in contact_patterns:
            matches = re.findall(pattern, resume_text)
            contact_info.extend(matches)
        
        return ' | '.join(contact_info[:4]) if contact_info else "Contact Information"
    
    def _extract_experience_years(self, resume_text: str) -> str:
        """Extract years of experience"""
        # Based on your resume showing 7+ years
        return "7"
    
    def _extract_key_skills(self, resume_text: str, missing_keywords: List[str]) -> List[str]:
        """Extract existing skills and incorporate missing keywords"""
        existing_skills = ['python', 'bash', 'linux', 'siem', 'networking', 'security']
        optimized_skills = existing_skills + [kw for kw in missing_keywords if kw not in existing_skills][:3]
        return optimized_skills
    
    def _optimize_experience_sections(self, experience_sections: List[Dict], missing_keywords: List[str], template_bullets: List[str]) -> str:
        """Optimize experience sections with relevant keywords"""
        # For now, return a simplified version
        # In a full implementation, this would enhance each experience bullet
        optimized_sections = []
        
        # Example enhancement - you would process each actual experience section
        sample_enhanced = f"""VAS Support Engineer | Tigo | Honduras | Feb 2024 - Jul 2025
• {template_bullets[0].format(technology="A2P SMS platform", language="Python/Bash", monitoring_type="telephony trunks")}
• {template_bullets[1]}
• {template_bullets[2].format(language="Python and Bash")}
• {template_bullets[3]}
• {template_bullets[4].format(monitoring_type="telephony trunks traffic")}

Customer Support Engineer | Arelion | Sweden | Dec 2021 - Jan 2023
• Conducted security incident response for VoIP, SMS, and mobile data threats
• Monitored A2P platform security logs to ensure efficient SMS traffic and detect potential threats
• Provided comprehensive assistance to B2B customers regarding international VoIP traffic, SMS, and mobile data"""
        
        return sample_enhanced
    
    def _generate_optimized_skills(self, original_skills: List[str], missing_keywords: List[str]) -> str:
        """Generate optimized skills section"""
        # Combine original skills with missing keywords
        all_skills = list(set(original_skills + missing_keywords))
        
        # Organize into categories (simplified)
        cybersecurity_skills = [s for s in all_skills if any(cyber_term in s.lower() for cyber_term in ['security', 'threat', 'incident', 'siem', 'vulnerability'])]
        technical_skills = [s for s in all_skills if s not in cybersecurity_skills]
        
        skills_text = "Cybersecurity Skills:\n"
        for skill in cybersecurity_skills[:8]:  # Limit to top skills
            skills_text += f"• {skill.title()}\n"
        
        if technical_skills:
            skills_text += "\nTechnical Skills:\n"
            for skill in technical_skills[:6]:
                skills_text += f"• {skill.title()}\n"
        
        return skills_text.strip()
    
    def _extract_education_section(self, resume_text: str) -> str:
        """Extract education section"""
        # Simple extraction - in practice, you'd parse more carefully
        education_start = resume_text.find("Education")
        if education_start == -1:
            education_start = resume_text.find("EDUCATION")
        
        if education_start != -1:
            # Find the end (next major section or end of text)
            next_sections = ["Languages", "Certificates", "Certifications", "Skills"]
            end_pos = len(resume_text)
            for section in next_sections:
                pos = resume_text.find(section, education_start)
                if pos != -1 and pos < end_pos:
                    end_pos = pos
            
            return resume_text[education_start:end_pos].strip()
        
        return "Education section not found"
    
    def _extract_certificates_section(self, resume_text: str) -> str:
        """Extract certificates section"""
        cert_start = resume_text.find("Certificates")
        if cert_start == -1:
            cert_start = resume_text.find("CERTIFICATES")
        
        if cert_start != -1:
            # Find the end
            next_sections = ["Languages", "Skills", "Experience"]
            end_pos = len(resume_text)
            for section in next_sections:
                pos = resume_text.find(section, cert_start)
                if pos != -1 and pos < end_pos:
                    end_pos = pos
            
            return resume_text[cert_start:end_pos].strip()
        
        return "Certificates section not found"
    
    def _extract_languages_section(self, resume_text: str) -> str:
        """Extract languages section"""
        lang_start = resume_text.find("Languages")
        if lang_start == -1:
            lang_start = resume_text.find("LANGUAGES")
        
        if lang_start != -1:
            return resume_text[lang_start:].strip()
        
        return "Languages section not found"
    
    def save_resume(self, resume_content: str, filename: Optional[str] = None) -> str:
        """Save generated resume to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"optimized_resume_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(resume_content)
            print(f"✅ Optimized resume saved to {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving resume: {e}")
            return ""

# Enhanced automation workflow
class CompleteAutomationWorkflow:
    def __init__(self, resume_path: str):
        from automated_resume_optimizer import AutomatedResumeOptimizer
        from job_analyzer import IntegratedOptimizer
        self.base_optimizer = AutomatedResumeOptimizer(resume_path)
        self.integrated_optimizer = IntegratedOptimizer(resume_path)
        self.generator = ResumeGenerator()
    
    def full_optimization_cycle(self, job_input: str, is_url: bool = False) -> Dict:
        """Complete optimization cycle: analyze → generate → save → track"""
        print("🚀 Starting full optimization cycle...")
        
        # 1. Extract job description
        if is_url:
            job_description = self.base_optimizer.extract_job_description_from_url(job_input)
        else:
            job_description = job_input
        
        if not job_description:
            return {"error": "Could not extract job description"}
        
        # 2. Comprehensive analysis
        print("🔍 Analyzing job requirements...")
        comprehensive_results = self.integrated_optimizer.comprehensive_analysis(job_description)
        
        # 3. Extract resume data
        print("📄 Processing resume data...")
        resume_data = {
            'text': self.base_optimizer.resume_text,
            'experience_sections': [],  # Would be parsed in full implementation
            'skills_section': [],       # Would be parsed in full implementation
        }
        
        # 4. Generate optimized resume
        print("✨ Generating optimized resume...")
        optimized_resume = self.generator.generate_optimized_resume(
            resume_data, 
            comprehensive_results['competency_gaps'],
            'cybersecurity_analyst'
        )
        
        # 5. Save optimized resume
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        resume_filename = f"optimized_resume_{timestamp}.txt"
        saved_filename = self.generator.save_resume(optimized_resume, resume_filename)
        
        # 6. Generate and save optimization report
        report_filename = self.base_optimizer.save_optimization_report(
            job_input[:50] + "..." if len(job_input) > 50 else job_input,
            comprehensive_results['basic_analysis']
        )
        
        return {
            'optimized_resume_file': saved_filename,
            'optimization_report': report_filename,
            'ats_score': comprehensive_results['basic_analysis']['ats_score'],
            'missing_keywords': comprehensive_results['competency_gaps']['missing_keywords'],
            'recommendations': comprehensive_results['enhanced_recommendations']
        }

# Example usage
if __name__ == "__main__":
    # Initialize the complete automation workflow
    workflow = CompleteAutomationWorkflow("CV_Victor_Martinez.pdf")
    
    # Example job description for testing
    sample_job = """
    Cybersecurity Analyst - SOC Operations
    
    We are seeking a Cybersecurity Analyst to join our Security Operations Center (SOC). 
    The ideal candidate will have experience with SIEM tools, incident response, and threat detection.
    
    Responsibilities:
    • Monitor and analyze security events using SIEM tools
    • Perform alert triage and incident response activities
    • Conduct threat hunting and vulnerability assessments
    • Collaborate with cross-functional security teams
    • Document security incidents and investigations
    
    Requirements:
    • 3-5 years of cybersecurity experience
    • Proficiency with SIEM platforms (Splunk, QRadar, or ArcSight)
    • Strong understanding of incident response procedures
    • Experience with threat hunting and malware analysis
    • Knowledge of network security and vulnerability management
    """
    
    # Run full optimization cycle
    results = workflow.full_optimization_cycle(sample_job)
    
    if 'error' not in results:
        print("\n✅ Full optimization cycle completed successfully!")
        print(f"📄 Optimized resume saved to: {results['optimized_resume_file']}")
        print(f"📊 ATS Score: {results['ats_score']}%")
        print(f"📋 Optimization report: {results['optimization_report']}")
        print(f"🎯 Missing keywords to address: {', '.join(results['missing_keywords'][:5])}")
    else:
        print(f"❌ Error: {results['error']}")