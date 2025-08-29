# main_automation.py
import sys
import argparse
from automated_resume_optimizer import AutomatedResumeOptimizer
from resume_template_manager import ResumeAutomationController

def main():
    parser = argparse.ArgumentParser(description='Automated Resume Optimizer')
    parser.add_argument('--resume', required=True, help='Path to your resume PDF')
    parser.add_argument('--job-url', help='URL of job posting to analyze')
    parser.add_argument('--job-file', help='Path to job description text file')
    parser.add_argument('--email', action='store_true', help='Send results via email')
    parser.add_argument('--track', action='store_true', help='Track this application')
    
    args = parser.parse_args()
    
    # Initialize automation controller
    controller = ResumeAutomationController(args.resume)
    
    if args.job_url:
        # Process job URL
        result = controller.process_job_application(args.job_url)
        if result:
            print(f"✅ Processed job: {args.job_url}")
            print(f"📊 ATS Score: {result['ats_score']}%")
            print(f"📄 Report: {result['report_file']}")
        else:
            print("❌ Failed to process job application")
            sys.exit(1)
    
    elif args.job_file:
        # Process job file
        with open(args.job_file, 'r') as f:
            job_description = f.read()
        
        optimizer = AutomatedResumeOptimizer(args.resume)
        suggestions = optimizer.generate_actionable_suggestions(job_description)
        report_file = optimizer.save_optimization_report(args.job_file, suggestions)
        print(f"✅ Processed job file: {args.job_file}")
        print(f"📊 ATS Score: {suggestions['ats_score']}%")
        print(f"📄 Report: {report_file}")
    
    else:
        print("Please provide either --job-url or --job-file")
        sys.exit(1)

if __name__ == "__main__":
    main()