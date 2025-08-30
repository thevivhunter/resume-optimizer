# main.py
import sys
import argparse
from datetime import datetime
from typing import Dict, Any
from automated_resume_optimizer import AutomatedResumeOptimizer
from job_analyzer import IntegratedOptimizer
from resume_generator import CompleteAutomationWorkflow
from application_tracker import ApplicationTracker

class ResumeOptimizerApp:
    def __init__(self, resume_path: str):
        self.resume_path = resume_path
        self.resume_text = self._extract_resume_text()
        self.workflow = CompleteAutomationWorkflow(resume_path)
        self.tracker = ApplicationTracker()
        self.job_analyzer = IntegratedOptimizer(resume_path)
    
    def _extract_resume_text(self) -> str:
        """Extract resume text using the base optimizer"""
        try:
            with open(self.resume_path, 'rb') as file:
                import PyPDF2
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.lower()
        except Exception as e:
            print(f"Error reading resume: {e}")
            return ""
    
    def analyze_job(self, job_input: str, is_url: bool = False) -> Dict[str, Any]:
        """Analyze a job description and provide optimization suggestions"""
        print("🔍 Analyzing job requirements...")
        
        # Extract job description
        if is_url:
            from automated_resume_optimizer import AutomatedResumeOptimizer
            optimizer = AutomatedResumeOptimizer(self.resume_path)
            job_description = optimizer.extract_job_description_from_url(job_input)
        else:
            job_description = job_input
        
        if not job_description:
            return {"error": "Could not extract job description"}
        
        # Comprehensive analysis
        results = self.job_analyzer.comprehensive_analysis(job_description)
        
        # Display results
        self._display_analysis_results(results, job_input)
        
        return results
    
    def optimize_for_job(self, job_input: str, is_url: bool = False, job_title: str = "", company: str = "") -> Dict[str, Any]:
        """Complete optimization cycle for a job application"""
        print("🚀 Starting complete optimization cycle...")
        
        # Run full optimization
        results = self.workflow.full_optimization_cycle(job_input, is_url)
        
        if 'error' in results:
            return results
        
        # Log application if job details provided
        if job_title and company:
            app_id = self.tracker.log_application(
                job_title=job_title,
                company=company,
                job_url=job_input if is_url else "Text description",
                ats_score=results['ats_score'],
                missing_keywords=results['missing_keywords'],
                resume_version=self.resume_path
            )
            results['application_id'] = app_id
        
        # Display summary
        self._display_optimization_summary(results)
        
        return results
    
    def show_application_stats(self):
        """Display job application statistics"""
        stats = self.tracker.get_summary_statistics()
        
        print("\n" + "="*50)
        print("JOB APPLICATION STATISTICS")
        print("="*50)
        print(f"📊 Total Applications: {stats['total_applications']}")
        print(f"🎯 Success Rate: {stats['success_rate']}%")
        
        if stats['status_breakdown']:
            print("\nStatus Breakdown:")
            for status, count in stats['status_breakdown'].items():
                print(f"  • {status.title()}: {count}")
        
        return stats
    
    def _display_analysis_results(self, results: Dict, job_source: str):
        """Display analysis results in a formatted way"""
        print("\n" + "="*60)
        print("RESUME OPTIMIZATION ANALYSIS")
        print("="*60)
        print(f"Job Source: {job_source[:50]}{'...' if len(job_source) > 50 else ''}")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📄 Resume: {self.resume_path}")
        
        basic = results['basic_analysis']
        gaps = results['competency_gaps']
        
        print(f"\n📊 ATS Compatibility Score: {basic['ats_score']}%")
        print(f"🎯 Match Percentage: {gaps['match_percentage']:.1f}%")
        
        print(f"\n✅ Matching Keywords: {len(gaps['matching_keywords'])}")
        if gaps['matching_keywords']:
            print("  " + ", ".join([f"'{kw}'" for kw in gaps['matching_keywords'][:8]]))
            if len(gaps['matching_keywords']) > 8:
                print(f"  ... and {len(gaps['matching_keywords']) - 8} more")
        
        print(f"\n❌ Missing Keywords: {len(gaps['missing_keywords'])}")
        if gaps['missing_keywords']:
            print("  " + ", ".join([f"'{kw}'" for kw in gaps['missing_keywords'][:8]]))
            if len(gaps['missing_keywords']) > 8:
                print(f"  ... and {len(gaps['missing_keywords']) - 8} more")
        
        print(f"\n💡 Recommendations:")
        for rec in results['enhanced_recommendations']:
            print(f"  • {rec}")
    
    def _display_optimization_summary(self, results: Dict):
        """Display optimization summary"""
        print("\n" + "="*60)
        print("OPTIMIZATION COMPLETED!")
        print("="*60)
        print(f"📄 Optimized Resume: {results['optimized_resume_file']}")
        print(f"📊 ATS Score: {results['ats_score']}%")
        print(f"📋 Report: {results['optimization_report']}")
        
        if 'application_id' in results:
            print(f"📌 Application ID: {results['application_id']}")
        
        if results['missing_keywords']:
            print(f"\n🎯 Still Missing Keywords:")
            for kw in results['missing_keywords'][:5]:
                print(f"  • {kw}")
    
    def run_interactive_mode(self):
        """Run in interactive mode"""
        print("Welcome to Resume Optimizer!")
        print("Commands: analyze, optimize, stats, help, quit")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    print("Goodbye!")
                    break
                elif command == 'help':
                    print("Available commands:")
                    print("  analyze [url/text] - Analyze a job description")
                    print("  optimize [url/text] - Optimize for a job")
                    print("  stats - Show application statistics")
                    print("  help - Show this help")
                    print("  quit - Exit the application")
                elif command == 'stats':
                    self.show_application_stats()
                elif command.startswith('analyze'):
                    self._handle_analyze_command(command)
                elif command.startswith('optimize'):
                    self._handle_optimize_command(command)
                else:
                    print("Unknown command. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _handle_analyze_command(self, command: str):
        """Handle analyze command"""
        parts = command.split(' ', 2)
        if len(parts) < 3:
            print("Usage: analyze [url/text] [job_url_or_text]")
            return
        
        input_type = parts[1]
        job_input = parts[2]
        
        if input_type == 'url':
            self.analyze_job(job_input, is_url=True)
        elif input_type == 'text':
            self.analyze_job(job_input, is_url=False)
        else:
            print("Input type must be 'url' or 'text'")
    
    def _handle_optimize_command(self, command: str):
        """Handle optimize command"""
        parts = command.split(' ', 4)
        if len(parts) < 5:
            print("Usage: optimize [url/text] [job_url_or_text] [job_title] [company]")
            return
        
        input_type = parts[1]
        job_input = parts[2]
        job_title = parts[3]
        company = parts[4]
        
        if input_type == 'url':
            self.optimize_for_job(job_input, is_url=True, job_title=job_title, company=company)
        elif input_type == 'text':
            self.optimize_for_job(job_input, is_url=False, job_title=job_title, company=company)
        else:
            print("Input type must be 'url' or 'text'")

# Command-line interface
def main():
    parser = argparse.ArgumentParser(description='Resume Optimizer Tool')
    parser.add_argument('--resume', required=True, help='Path to your resume PDF')
    parser.add_argument('--job-url', help='URL of job posting to analyze')
    parser.add_argument('--job-text', help='Path to job description text file')
    parser.add_argument('--job-title', help='Job title for tracking')
    parser.add_argument('--company', help='Company name for tracking')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--stats', action='store_true', help='Show application statistics')
    
    args = parser.parse_args()
    
    # Initialize the application
    app = ResumeOptimizerApp(args.resume)
    
    if args.interactive:
        app.run_interactive_mode()
    elif args.stats:
        app.show_application_stats()
    elif args.job_url:
        if args.job_title and args.company:
            app.optimize_for_job(args.job_url, is_url=True, job_title=args.job_title, company=args.company)
        else:
            app.analyze_job(args.job_url, is_url=True)
    elif args.job_text:
        try:
            with open(args.job_text, 'r') as f:
                job_text = f.read()
            
            if args.job_title and args.company:
                app.optimize_for_job(job_text, is_url=False, job_title=args.job_title, company=args.company)
            else:
                app.analyze_job(job_text, is_url=False)
        except Exception as e:
            print(f"Error reading job text file: {e}")
    else:
        print("Please provide either --job-url, --job-text, --interactive, or --stats")
        parser.print_help()

if __name__ == "__main__":
    main()