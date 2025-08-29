# resume_template_manager.py
import json
from datetime import datetime
from typing import Dict, List

class ResumeTemplateManager:
    def __init__(self):
        self.templates = {
            'cybersecurity_analyst': {
                'title': 'Cybersecurity Analyst',
                'summary_template': '''Cybersecurity Analyst with {years}+ years of experience in {skill1}, {skill2}, and {skill3}. Skilled in {skill4}, {skill5}, and telecommunications infrastructure security. Experienced in {skill6} and customer-focused cybersecurity support.''',
                'experience_keywords': ['security', 'incident', 'response', 'threat', 'detection', 'siem'],
                'skills_section': [
                    'Security Information & Event Management (SIEM)',
                    'Threat Detection and Monitoring', 
                    'Security Incident Response',
                    'Network Security Analysis',
                    'Vulnerability Assessment',
                    'Python/Bash Automation',
                    'Linux System Management'
                ]
            },
            'soc_analyst': {
                'title': 'SOC Cybersecurity Analyst',
                'summary_template': '''SOC Cybersecurity Analyst with {years}+ years of experience in threat detection, security monitoring, and incident response. Proficient in SIEM operations, alert triage, and security investigations. Skilled in {skill1} and {skill2}.''',
                'experience_keywords': ['triage', 'hunt', 'intelligence', 'malware', 'forensics', 'monitoring'],
                'skills_section': [
                    'Security Information & Event Management (SIEM)',
                    'Threat Hunting and Intelligence',
                    'Alert Triage and Investigation',
                    'Incident Response and Forensics',
                    'Malware Analysis',
                    'Security Monitoring',
                    'Threat Detection'
                ]
            }
        }
    
    def generate_optimized_resume_content(self, original_resume_text: str, missing_keywords: List[str], template_type: str = 'cybersecurity_analyst') -> Dict:
        """Generate optimized resume content based on missing keywords"""
        template = self.templates.get(template_type, self.templates['cybersecurity_analyst'])
        
        # Extract key information from original resume
        experience_years = self._extract_experience_years(original_resume_text)
        key_skills = self._extract_key_skills(original_resume_text, missing_keywords)
        
        # Generate optimized content
        optimized_summary = template['summary_template'].format(
            years=experience_years,
            skill1=key_skills[0] if len(key_skills) > 0 else "network security",
            skill2=key_skills[1] if len(key_skills) > 1 else "threat detection", 
            skill3=key_skills[2] if len(key_skills) > 2 else "incident response",
            skill4=key_skills[3] if len(key_skills) > 3 else "SIEM operations",
            skill5=key_skills[4] if len(key_skills) > 4 else "security monitoring",
            skill6=key_skills[5] if len(key_skills) > 5 else "security investigations"
        )
        
        return {
            'title': template['title'],
            'summary': optimized_summary,
            'skills': template['skills_section'],
            'experience_keywords_to_add': template['experience_keywords']
        }
    
    def _extract_experience_years(self, resume_text: str) -> str:
        """Extract years of experience from resume text"""
        # Simple extraction - you can make this more sophisticated
        return "7"  # Based on your resume showing 7+ years
    
    def _extract_key_skills(self, resume_text: str, missing_keywords: List[str]) -> List[str]:
        """Extract existing skills and incorporate missing keywords"""
        # Combine existing skills with missing keywords for optimization
        existing_skills = ['python', 'bash', 'linux', 'siem', 'networking']
        optimized_skills = existing_skills + [kw for kw in missing_keywords if kw not in existing_skills][:3]
        return optimized_skills

# Application tracking system
class ApplicationTracker:
    def __init__(self, tracking_file: str = "application_tracking.json"):
        self.tracking_file = tracking_file
        self.applications = self._load_tracking_data()
    
    def _load_tracking_data(self) -> Dict:
        """Load existing tracking data"""
        try:
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def log_application(self, job_url: str, ats_score: float, missing_keywords: List[str], resume_version: str):
        """Log job application details"""
        application_id = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.applications[application_id] = {
            'timestamp': datetime.now().isoformat(),
            'job_url': job_url,
            'ats_score': ats_score,
            'missing_keywords': missing_keywords,
            'resume_version': resume_version,
            'status': 'applied'
        }
        
        self._save_tracking_data()
        return application_id
    
    def _save_tracking_data(self):
        """Save tracking data to file"""
        with open(self.tracking_file, 'w') as f:
            json.dump(self.applications, f, indent=2)
    
    def get_success_rate(self) -> Dict:
        """Calculate success rate based on tracked applications"""
        total_apps = len(self.applications)
        if total_apps == 0:
            return {'total_applications': 0, 'success_rate': 0}
        
        # For now, we'll simulate success tracking
        # In real implementation, you'd update application statuses manually or via email tracking
        successful_apps = sum(1 for app in self.applications.values() 
                            if app.get('status') == 'interview' or app.get('status') == 'offer')
        
        return {
            'total_applications': total_apps,
            'successful_applications': successful_apps,
            'success_rate': round((successful_apps / total_apps) * 100, 1) if total_apps > 0 else 0
        }

# Main automation controller
class ResumeAutomationController:
    def __init__(self, resume_path: str):
        self.optimizer = AutomatedResumeOptimizer(resume_path)
        self.template_manager = ResumeTemplateManager()
        self.tracker = ApplicationTracker()
    
    def process_job_application(self, job_url: str, email_config: Dict = None):
        """Complete automation workflow for a job application"""
        print(f"Processing job application for: {job_url}")
        
        # 1. Extract job description
        job_description = self.optimizer.extract_job_description_from_url(job_url)
        if not job_description:
            print("Could not extract job description")
            return None
        
        # 2. Analyze resume-job match
        suggestions = self.optimizer.generate_actionable_suggestions(job_description)
        
        # 3. Generate optimized resume content
        optimized_content = self.template_manager.generate_optimized_resume_content(
            self.optimizer.resume_text, 
            suggestions['missing_keywords']
        )
        
        # 4. Log application
        app_id = self.tracker.log_application(
            job_url, 
            suggestions['ats_score'], 
            suggestions['missing_keywords'],
            "optimized_version"
        )
        
        # 5. Save optimization report
        report_file = self.optimizer.save_optimization_report(job_url, suggestions)
        
        # 6. Send email notification (if configured)
        if email_config:
            self.optimizer.send_optimization_report(job_url, suggestions, email_config)
        
        # 7. Return results
        return {
            'application_id': app_id,
            'ats_score': suggestions['ats_score'],
            'missing_keywords': suggestions['missing_keywords'],
            'optimized_content': optimized_content,
            'report_file': report_file
        }

# Example usage
if __name__ == "__main__":
    # Initialize the automation controller
    controller = ResumeAutomationController("CV_Victor_Martinez.pdf")
    
    # Example job URL processing
    sample_job_url = "https://www.linkedin.com/jobs/view/cybersecurity-analyst-at-company"
    
    # Process the job application (this would be the main automation workflow)
    result = controller.process_job_application(sample_job_url)
    
    if result:
        print("Job application processed successfully!")
        print(f"ATS Score: {result['ats_score']}%")
        print(f"Application ID: {result['application_id']}")
        print(f"Report saved to: {result['report_file']}")