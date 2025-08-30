# complete_workflow.py
from automated_resume_optimizer import AutomatedResumeOptimizer
from application_tracker import ApplicationTracker

def run_complete_optimization(resume_path, job_url):
    """Complete end-to-end optimization workflow"""
    # Initialize components
    optimizer = AutomatedResumeOptimizer(resume_path)
    tracker = ApplicationTracker()
    
    # 1. Analyze job description
    job_description = optimizer.extract_job_description_from_url(job_url)
    
    # 2. Generate optimization suggestions
    suggestions = optimizer.generate_actionable_suggestions(job_description)
    
    # 3. Save optimization report
    report_file = optimizer.save_optimization_report(job_url, suggestions)
    
    # 4. Log application
    tracker.log_application(
        job_title="Cybersecurity Analyst",  # Would extract from job description
        company="Tech Company",  # Would extract from job description
        job_url=job_url,
        ats_score=suggestions['ats_score'],
        missing_keywords=suggestions['missing_keywords'],
        resume_version=resume_path,
        status="applied"
    )
    
    return {
        'ats_score': suggestions['ats_score'],
        'missing_keywords': suggestions['missing_keywords'],
        'report_file': report_file
    }

# Example usage
if __name__ == "__main__":
    results = run_complete_optimization(
        "CV_Victor_Martinez.pdf",
        "https://www.tecoloco.com.hn/998908/jefe-de-soporte"
    )
    
    print(f"Optimization completed with ATS score: {results['ats_score']}%")
    print(f"Report saved to: {results['report_file']}")