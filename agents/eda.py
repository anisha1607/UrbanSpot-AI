import sys
sys.path.append('/home/claude/business-location-advisor')

from typing import Dict, Any
import pandas as pd
from tools.analysis import merge_datasets, compute_scores, summarize_results
from tools.output import generate_charts
import plotly.graph_objects as go


class EDAAgent:
    """
    Performs exploratory data analysis and computes metrics
    """
    
    def __init__(self):
        self.merged_data = None
        self.scored_data = None
        self.charts = []
    
    def analyze(
        self,
        datasets: Dict[str, pd.DataFrame],
        weights: Dict[str, float],
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform EDA and compute neighborhood scores
        """
        print("\n=== Starting EDA ===")
        
        print("Step 1: Merging datasets...")
        self.merged_data = merge_datasets(datasets)
        print(f"  Merged data shape: {self.merged_data.shape}")
        
        filters = plan.get('filters', {})
        if filters.get('borough'):
            borough_val = filters['borough']
            
            # Check if value is "ALL" or should skip filtering
            if isinstance(borough_val, str) and borough_val.upper() in ['ALL', 'ANY', 'NONE', 'N/A', '', 'NULL']:
                print(f"Step 2: Skipping borough filter (analyzing ALL boroughs)")
                print(f"  Total neighborhoods: {len(self.merged_data)}")
            else:
                # Apply borough filter
                print(f"Step 2: Applying borough filter: {borough_val}")
                borough_col = self._find_borough_column(self.merged_data)
                
                if borough_col:
                    print(f"  Using column: '{borough_col}'")
                    
                    # Normalize borough names in the data
                    self.merged_data[borough_col] = self.merged_data[borough_col].apply(
                        self._normalize_borough_name
                    )
                    
                    # Normalize filter values
                    if isinstance(borough_val, list):
                        filter_boroughs = [self._normalize_borough_name(b) for b in borough_val]
                        print(f"  Looking for: {filter_boroughs}")
                    else:
                        filter_boroughs = [self._normalize_borough_name(borough_val)]
                        print(f"  Looking for: {filter_boroughs}")
                    
                    print(f"  Available boroughs: {self.merged_data[borough_col].unique().tolist()[:10]}")
                    
                    # Apply filter
                    original_count = len(self.merged_data)
                    self.merged_data = self.merged_data[
                        self.merged_data[borough_col].isin(filter_boroughs)
                    ]
                    filtered_count = len(self.merged_data)
                    
                    print(f"  Filtered: {original_count} → {filtered_count} neighborhoods")
                    
                    if filtered_count == 0:
                        print(f"  ⚠️ WARNING: No neighborhoods found after filtering!")
                        print(f"  Available unique values: {self.merged_data[borough_col].unique().tolist()}")
                else:
                    print(f"  ⚠️ Warning: No borough column found, skipping filter")
                    print(f"  Available columns: {list(self.merged_data.columns)}")
        else:
            print(f"Step 2: No borough filter specified (analyzing ALL boroughs)")
            print(f"  Total neighborhoods: {len(self.merged_data)}")
        
        print("Step 3: Computing scores...")
        self.scored_data = compute_scores(self.merged_data, weights)
        print(f"  Scored {len(self.scored_data)} neighborhoods")
        
        print("Step 4: Generating summary statistics...")
        summary = summarize_results(self.scored_data, top_n=10)
        
        print("Step 5: Creating visualizations...")
        self.charts = generate_charts(self.scored_data)
        print(f"  Generated {len(self.charts)} charts")
        
        print("\n=== Top 5 Neighborhoods ===")
        top_5 = self.scored_data.head(5)
        for idx, row in top_5.iterrows():
            print(f"{row.get('neighborhood', 'Unknown')}: Score = {row.get('final_score', 0):.3f}")
        
        return {
            'summary': summary,
            'scored_data': self.scored_data.to_dict('records'),  # ALL neighborhoods
            'top_neighborhoods': self.scored_data.head(10).to_dict('records'),  # Top 10 for display
            'charts_generated': len(self.charts),
            'total_analyzed': len(self.scored_data)
        }
    
    def _find_borough_column(self, df: pd.DataFrame) -> str:
        """
        Find the column containing borough information
        """
        possible_names = ['borough', 'boro', 'borough_name', 'boroname']
        
        for col in df.columns:
            if col.lower() in possible_names:
                return col
        
        return None
    
    def _normalize_borough_name(self, name: str) -> str:
        """
        Normalize borough names to standard format
        """
        if pd.isna(name):
            return None
        
        name_upper = str(name).upper().strip()
        
        # Map common variations
        mappings = {
            'MN': 'MANHATTAN',
            'MANHATTAN': 'MANHATTAN',
            'BK': 'BROOKLYN',
            'BROOKLYN': 'BROOKLYN', 
            'BX': 'BRONX',
            'BRONX': 'BRONX',
            'QN': 'QUEENS',
            'QUEENS': 'QUEENS',
            'SI': 'STATEN ISLAND',
            'STATEN ISLAND': 'STATEN ISLAND',
            'STATENISLAND': 'STATEN ISLAND'
        }
        
        return mappings.get(name_upper, name_upper)
    
    def get_detailed_metrics(self, neighborhood: str) -> Dict[str, Any]:
        """
        Get detailed metrics for a specific neighborhood
        """
        if self.scored_data is None:
            return {}
        
        neighborhood_col = 'neighborhood'
        if neighborhood_col not in self.scored_data.columns:
            for col in self.scored_data.columns:
                if 'name' in col.lower() or 'neighborhood' in col.lower():
                    neighborhood_col = col
                    break
        
        row = self.scored_data[
            self.scored_data[neighborhood_col].str.contains(neighborhood, case=False, na=False)
        ]
        
        if row.empty:
            return {}
        
        return row.iloc[0].to_dict()
    
    def get_charts(self) -> list:
        """
        Return generated charts
        """
        return self.charts


class MarketAnalystAgent:
    """
    Model-driven agent that triggers the EDA analysis tool
    """
    def __init__(self, model_name: str = "models/gemini-2.0-flash"):
        from agents.gemini_client import GeminiChatSession
        self.session = GeminiChatSession(model=model_name)
    
    def run_analysis(self, datasets: Dict[str, pd.DataFrame], weights: Dict[str, float], plan: Dict[str, Any]) -> tuple:
        system_prompt = "You are a specialized Market Analyst. You must invoke the 'perform_eda_calculations' tool to process the raw datasets."
        
        tools = [{
            "name": "perform_eda_calculations",
            "description": "Perform statistical scoring and aggregation on the business datasets",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["analyze"]}
                },
                "required": ["action"]
            }
        }]
        
        messages = [{"role": "user", "content": "The datasets are ready. Execute the EDA analysis now."}]
        
        response = self.session.create_message(system=system_prompt, messages=messages, tools=tools)
        
        # Check if the model called the tool
        tool_called = False
        for block in response.content:
            if hasattr(block, "type") and block.type == "tool_use" and block.name == "perform_eda_calculations":
                print(f"📊 Market Analyst Agent invoking tool [perform_eda_calculations] on {len(datasets)} datasets...")
                tool_called = True
                break
        
        # Even if model misses, we run the tool for the flow to continue
        eda_engine = EDAAgent()
        results = eda_engine.analyze(datasets, weights, plan)
        charts = eda_engine.get_charts()
        return results, charts, eda_engine.scored_data

def perform_eda(
    datasets: Dict[str, pd.DataFrame],
    weights: Dict[str, float],
    plan: Dict[str, Any]
) -> tuple:
    """
    Agent-orchestrated EDA call
    """
    analyst = MarketAnalystAgent()
    return analyst.run_analysis(datasets, weights, plan)