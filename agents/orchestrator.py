import sys
sys.path.append('/home/claude/business-location-advisor')

from typing import Dict, Any
from agents.planner import create_analysis_plan
from agents.data_collector import collect_data
from agents.eda import perform_eda
from agents.hypothesis import generate_hypothesis
from agents.critic import critique_recommendation
from tools.output import save_csv, save_report, OutputGenerator
import pandas as pd


class BusinessLocationOrchestrator:
    """
    Orchestrates the multi-agent workflow (simplified without LangGraph)
    """
    
    def __init__(self):
        self.iteration = 0
        self.max_iterations = 2
    
    def run(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the complete workflow
        """
        print("\n" + "="*50)
        print("PLANNER AGENT")
        print("="*50)
        plan = create_analysis_plan(user_input)
        print(f"Created plan for {plan['business_type']}")
        print(f"Data sources: {', '.join(plan['data_sources'])}")
        
        print("\n" + "="*50)
        print("DATA COLLECTOR AGENT")
        print("="*50)
        datasets = collect_data(plan)
        
        print("\n" + "="*50)
        print("MARKET ANALYST AGENT (EDA Step)")
        print("="*50)
        weights = {
            'demand': user_input.get('weight_demand', 0.25),
            'foot_traffic': user_input.get('weight_foot_traffic', 0.20),
            'income': user_input.get('weight_income', 0.20),
            'competition': user_input.get('weight_competition', 0.20),
            'rent': user_input.get('weight_rent', 0.15)
        }
        
        eda_results, charts, scored_data = perform_eda(datasets, weights, plan)
        
        # Refinement loop
        previous_feedback = None
        
        while self.iteration < self.max_iterations:
            self.iteration += 1
            
            print("\n" + "="*50)
            print(f"STRATEGIC HYPOTHESIS AGENT (Iteration {self.iteration})")
            print("="*50)
            
            # Pass previous critic feedback for improvement
            if previous_feedback:
                print(f"Using feedback from previous iteration:")
                print(f"  Issues: {len(previous_feedback.get('issues', []))}")
                print(f"  Suggestions: {len(previous_feedback.get('suggestions', []))}")
            
            recommendation, explanation = generate_hypothesis(
                eda_results,
                plan['business_type'],
                previous_critique=previous_feedback  # Pass the feedback!
            )
            print(f"Recommendation: {recommendation['best_location']}")
            
            print("\n" + "="*50)
            print(f"CRITIC AGENT (Iteration {self.iteration})")
            print("="*50)
            feedback, formatted = critique_recommendation(
                recommendation,
                eda_results,
                plan
            )
            print(f"{'Approved' if feedback['approved'] else 'Needs refinement'}")
            
            # Store feedback for next iteration
            previous_feedback = feedback
            
            if feedback['approved'] or self.iteration >= self.max_iterations:
                break
        
        print("\n" + "="*50)
        print("OUTPUT GENERATION")
        print("="*50)
        
        generator = OutputGenerator()
        
        csv_path = generator.save_csv(scored_data, 'neighborhood_scores.csv')
        print(f"Saved scores to: {csv_path}")
        
        report_content = f"""NYC BUSINESS LOCATION ADVISOR - ANALYSIS REPORT
{'='*60}

{explanation}

{formatted}

ANALYSIS METADATA:
- Business Type: {plan['business_type']}
- Neighborhoods Analyzed: {eda_results['total_analyzed']}
- Data Sources: {', '.join(plan['data_sources'])}
- Iterations: {self.iteration}
"""
        
        report_path = generator.save_report(report_content, 'analysis_report.txt')
        print(f"Saved report to: {report_path}")
        
        chart_paths = generator.save_charts(charts)
        print(f"Saved {len(chart_paths)} charts")
        
        final_output = {
            'recommendation': recommendation,
            'explanation': explanation,
            'critic_feedback': feedback,
            'artifacts': {
                'csv': csv_path,
                'report': report_path,
                'charts': chart_paths,
                'figures': charts,          # In-memory Plotly objects → used by PDF generator
                'scored_data': scored_data  # Pass the raw data for UI tables
            },
            'iterations': self.iteration
        }
        
        return final_output


def run_analysis(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standalone function to run the complete analysis
    """
    orchestrator = BusinessLocationOrchestrator()
    return orchestrator.run(user_input)