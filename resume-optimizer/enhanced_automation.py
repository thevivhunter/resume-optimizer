# enhanced_automation.py
class AutomatedResumeOptimizer:
    def __init__(self):
        self.original_resume = "VICTOR MARTINEZ - Telecommunications and Cybersecurity Engineer Resume.pdf"
        self.optimized_resume = "CV_Victor_Martinez.pdf"
        self.job_description = "soc_analyst_job.txt"
    
    def compare_versions(self):
        """Automatically compare before/after optimization"""
        original_score = self.analyze_resume(self.original_resume)
        optimized_score = self.analyze_resume(self.optimized_resume)
        
        improvement = optimized_score - original_score
        return {
            'original_score': original_score,
            'optimized_score': optimized_score,
            'improvement': improvement,
            'percentage_improved': (improvement / original_score) * 100 if original_score > 0 else 0
        }
    
    def generate_job_specific_optimization(self, job_file):
        """Generate job-specific suggestions"""
        # Extract job keywords
        # Compare with both resume versions
        # Recommend which resume to use + additional keywords to add
        pass

# Run automated comparison
optimizer = AutomatedResumeOptimizer()
results = optimizer.compare_versions()
print(f"Improvement: {results['original_score']}% → {results['optimized_score']}% (+{results['improvement']}%)")