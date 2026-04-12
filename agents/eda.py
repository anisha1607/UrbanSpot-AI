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
            print(f"Step 2: Applying borough filter: {filters['borough']}")
            borough_col = self._find_borough_column(self.merged_data)
            if borough_col:
                # Normalize borough names in the data
                self.merged_data[borough_col] = self.merged_data[borough_col].apply(
                    self._normalize_borough_name
                )
                
                # Normalize filter values
                filter_boroughs = [self._normalize_borough_name(b) for b in filters['borough']]
                
                print(f"  Looking for: {filter_boroughs}")
                print(f"  Available: {self.merged_data[borough_col].unique().tolist()[:10]}")
                
                # Apply filter
                self.merged_data = self.merged_data[
                    self.merged_data[borough_col].isin(filter_boroughs)
                ]
                print(f"  Filtered data shape: {self.merged_data.shape}")
            else:
                print(f"  Warning: No borough column found, skipping filter")
        
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
            'top_neighborhoods': self.scored_data.head(10).to_dict('records'),
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


def perform_eda(
    datasets: Dict[str, pd.DataFrame],
    weights: Dict[str, float],
    plan: Dict[str, Any]
) -> tuple:
    """
    Standalone function to perform EDA
    Returns (analysis_results, charts)
    """
    eda_agent = EDAAgent()
    results = eda_agent.analyze(datasets, weights, plan)
    charts = eda_agent.get_charts()
    
    return results, charts, eda_agent.scored_data