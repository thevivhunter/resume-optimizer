# config.py
import os
from typing import Dict, Any

class Config:
    """Configuration for the resume optimizer"""
    
    # Paths
    RESUME_PATH = os.getenv('RESUME_PATH', 'CV_Victor_Martinez.pdf')
    TRACKING_FILE = os.getenv('TRACKING_FILE', 'job_applications.json')
    REPORTS_DIR = os.getenv('REPORTS_DIR', 'reports')
    
    # Job analysis
    MIN_ATS_SCORE = 70.0
    KEYWORD_CATEGORIES = {
        'core_skills': ['siem', 'incident', 'response', 'threat', 'detection', 'monitoring'],
        'tools': ['splunk', 'arcsight', 'qradar', 'sentinelone', 'defender'],
        'experience': ['analyst', 'soc', 'security operations', 'forensics', 'malware']
    }
    
    # Email settings (optional)
    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
    EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'your_email@gmail.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your_app_password')
    EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT', 'your_email@gmail.com')
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            'resume_path': cls.RESUME_PATH,
            'tracking_file': cls.TRACKING_FILE,
            'reports_dir': cls.REPORTS_DIR,
            'min_ats_score': cls.MIN_ATS_SCORE,
            'email_enabled': cls.EMAIL_ENABLED,
            'email_sender': cls.EMAIL_SENDER,
            'email_recipient': cls.EMAIL_RECIPIENT
        }