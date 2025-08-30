# enhanced_job_analyzer.py
import re
from typing import Dict, List
from collections import Counter

class EnhancedJobAnalyzer:
    def __init__(self):
        self.cybersecurity_keywords = {
            'core_skills': ['siem', 'incident', 'response', 'threat', 'detection', 'monitoring', 'vulnerability'],
            'tools': ['splunk', 'arcsight', 'qradar', 'sentinelone', 'defender', 'firewall', 'ids', 'ips'],
            'experience': ['analyst', 'soc', 'security operations', 'forensics', 'malware', 'triage'],
            'responsibilities': ['investigation', 'analysis', 'reporting', 'hunting', 'intelligence']
        }
    
    def analyze_job_url(self, url: str) -> Dict:
        """Enhanced analysis of job URL"""
        # This would extract and analyze the job posting
        # For now, returning sample structure
        return {
            'url': url,
            'position_type': self._identify_position_type(url),
            'required_skills': self._extract_required_skills(url),
            'experience_level': self._determine_experience_level(url)
        }
    
    def _identify_position_type(self, url: str) -> str:
        """Identify if job is SOC, Network Security, etc."""
        url_lower = url.lower()
        if 'soc' in url_lower or 'security operations' in url_lower:
            return 'soc_analyst'
        elif 'network' in url_lower or 'infrastructure' in url_lower:
            return 'network_security'
        elif 'penetration' in url_lower or 'pentest' in url_lower:
            return 'penetration_testing'
        else:
            return 'general_cybersecurity'
    
    def _extract_required_skills(self, url: str) -> List[str]:
        """Extract required skills from job URL"""
        # In a full implementation, this would scrape the actual job posting
        # For now, returning sample skills based on URL
        if 'soc' in url.lower():
            return ['siem', 'incident response', 'threat detection', 'log analysis', 'alert triage']
        else:
            return ['network security', 'vulnerability assessment', 'security monitoring', 'incident response']
    
    def _determine_experience_level(self, url: str) -> str:
        """Determine required experience level"""
        url_lower = url.lower()
        if 'senior' in url_lower or 'lead' in url_lower:
            return 'senior'
        elif 'junior' in url_lower or 'entry' in url_lower:
            return 'junior'
        else:
            return 'mid-level'

# Complete automation system
class CompleteResumeOptimizer:
    def __init__(self, resume_path: str):
        self.resume_path = resume_path
        self.job_analyzer = EnhancedJobAnalyzer()
        # Would integrate with existing optimizer components
    
    def optimize_for_position(self, job_url: str) -> Dict:
        """Complete optimization for a specific position"""
        # Analyze job requirements
        job_analysis = self.job_analyzer.analyze_job_url(job_url)
        
        # Generate position-specific recommendations
        recommendations = self._generate_position_specific_recommendations(job_analysis)
        
        return {
            'job_analysis': job_analysis,
            'recommendations': recommendations,
            'optimization_score': self._calculate_optimization_potential(job_analysis)
        }
    
    def _generate_position_specific_recommendations(self, job_analysis: Dict) -> List[str]:
        """Generate recommendations based on position type"""
        recommendations = []
        
        if job_analysis['position_type'] == 'soc_analyst':
            recommendations.append("🎯 Emphasize SIEM operations and security monitoring experience")
            recommendations.append("💡 Highlight incident response and alert triage capabilities")
            recommendations.append("📌 Add 'SOC' to your skills section if applicable")
        
        elif job_analysis['position_type'] == 'network_security':
            recommendations.append("🎯 Emphasize network security and infrastructure protection")
            recommendations.append("💡 Highlight firewall management and IDS/IPS experience")
        
        return recommendations
    
    def _calculate_optimization_potential(self, job_analysis: Dict) -> float:
        """Calculate potential improvement score"""
        # Simple calculation based on position type and experience level
        base_score = 50.0
        
        if job_analysis['position_type'] == 'soc_analyst':
            base_score += 20.0
        elif job_analysis['experience_level'] == 'junior':
            base_score += 15.0
        
        return min(base_score, 95.0)  # Cap at 95%

# Example usage
if __name__ == "__main__":
    optimizer = CompleteResumeOptimizer("CV_Victor_Martinez.pdf")
    
    # Test with the job URL you analyzed
    results = optimizer.optimize_for_position("https://www.tecoloco.com.hn/998908/jefe-de-soporte")
    
    print("=== POSITION-SPECIFIC OPTIMIZATION ===")
    print(f"Position Type: {results['job_analysis']['position_type']}")
    print(f"Experience Level: {results['job_analysis']['experience_level']}")
    print(f"Optimization Potential: {results['optimization_score']}%")
    
    print("\nRecommendations:")
    for rec in results['recommendations']:
        print(f"  • {rec}")