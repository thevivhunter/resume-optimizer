# application_tracker.py
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional

class ApplicationTracker:
    def __init__(self, tracking_file: str = "job_applications.json"):
        self.tracking_file = tracking_file
        self.applications = self._load_tracking_data()
    
    def _load_tracking_data(self) -> Dict:
        """Load existing tracking data"""
        try:
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"applications": []}
    
    def log_application(self, 
                       job_title: str, 
                       company: str, 
                       job_url: str,
                       ats_score: float,
                       missing_keywords: List[str],
                       resume_version: str,
                       status: str = "applied") -> str:
        """Log job application details"""
        application_id = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        application_data = {
            'id': application_id,
            'timestamp': datetime.now().isoformat(),
            'job_title': job_title,
            'company': company,
            'job_url': job_url,
            'ats_score': ats_score,
            'missing_keywords': missing_keywords,
            'resume_version': resume_version,
            'status': status,
            'follow_up_date': None
        }
        
        self.applications["applications"].append(application_data)
        self._save_tracking_data()
        
        print(f"✅ Application logged: {job_title} at {company}")
        return application_id
    
    def update_application_status(self, application_id: str, new_status: str, notes: str = ""):
        """Update application status"""
        for app in self.applications["applications"]:
            if app['id'] == application_id:
                app['status'] = new_status
                app['last_updated'] = datetime.now().isoformat()
                if notes:
                    if 'notes' not in app:
                        app['notes'] = []
                    app['notes'].append({
                        'timestamp': datetime.now().isoformat(),
                        'note': notes
                    })
                self._save_tracking_data()
                print(f"✅ Application status updated to: {new_status}")
                return
        
        print(f"❌ Application ID {application_id} not found")
    
    def _save_tracking_data(self):
        """Save tracking data to file"""
        with open(self.tracking_file, 'w') as f:
            json.dump(self.applications, f, indent=2)
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics of job applications"""
        total = len(self.applications["applications"])
        if total == 0:
            return {'total_applications': 0, 'success_rate': 0}
        
        # Count by status
        status_counts = {}
        for app in self.applications["applications"]:
            status = app['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate success rate (interviews and offers)
        successful = sum(1 for app in self.applications["applications"] 
                        if app['status'] in ['interview', 'offer', 'hired'])
        
        return {
            'total_applications': total,
            'successful_applications': successful,
            'success_rate': round((successful / total) * 100, 1),
            'status_breakdown': status_counts
        }
    
    def export_to_csv(self, filename: str = "job_applications_export.csv"):
        """Export application data to CSV"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'timestamp', 'job_title', 'company', 'job_url', 
                            'ats_score', 'status', 'resume_version', 'missing_keywords']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for app in self.applications["applications"]:
                    # Convert missing_keywords list to string
                    app_copy = app.copy()
                    app_copy['missing_keywords'] = ', '.join(app['missing_keywords'])
                    writer.writerow(app_copy)
            
            print(f"✅ Data exported to {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return None

# Example usage
if __name__ == "__main__":
    tracker = ApplicationTracker()
    
    # Log a sample application
    app_id = tracker.log_application(
        job_title="Cybersecurity Analyst",
        company="Tech Company",
        job_url="https://example.com/job/123",
        ats_score=76.5,
        missing_keywords=["splunk", "incident response", "threat hunting"],
        resume_version="CV_Victor_Martinez.pdf"
    )
    
    # Update status
    tracker.update_application_status(app_id, "interview", "Phone screen scheduled for Friday")
    
    # Get summary
    summary = tracker.get_summary_statistics()
    print(f"📊 Total Applications: {summary['total_applications']}")
    print(f"🎯 Success Rate: {summary['success_rate']}%")