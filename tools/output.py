import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict
import os
from datetime import datetime


class OutputGenerator:
    def __init__(self, output_dir: str = "data/outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_csv(self, df: pd.DataFrame, filename: str) -> str:
        """
        Save DataFrame to CSV
        """
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        return filepath
    
    def save_report(self, content: str, filename: str) -> str:
        """
        Save text report to file
        """
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def generate_charts(self, df: pd.DataFrame) -> List[go.Figure]:
        """
        Generate visualizations for the analysis
        """
        figures = []
        
        # Find the neighborhood/location column
        neighborhood_col = None
        for col in ['neighborhood', 'name', 'zipcode', 'location']:
            if col in df.columns:
                neighborhood_col = col
                break
        
        if not neighborhood_col and len(df) > 0:
            # Use index as neighborhood identifier
            df = df.copy()
            df['location'] = df.index.astype(str)
            neighborhood_col = 'location'
        
        if 'final_score' in df.columns and neighborhood_col and len(df) > 0:
            top_10 = df.head(10)
            
            fig1 = px.bar(
                top_10,
                x=neighborhood_col,
                y='final_score',
                title='Top 10 Neighborhoods by Score',
                labels={'final_score': 'Score', neighborhood_col: 'Neighborhood'},
                color='final_score',
                color_continuous_scale='Viridis'
            )
            fig1.update_layout(xaxis_tickangle=-45)
            figures.append(fig1)
        
        metric_cols = ['competition_count', 'median_income', 'median_rent', 'population']
        available_metrics = [col for col in metric_cols if col in df.columns]
        
        if available_metrics and neighborhood_col and len(df) > 0:
            top_10 = df.head(10)
            
            fig2 = go.Figure()
            
            for metric in available_metrics:
                normalized = (top_10[metric] - top_10[metric].min()) / (top_10[metric].max() - top_10[metric].min())
                
                fig2.add_trace(go.Scatter(
                    x=top_10[neighborhood_col],
                    y=normalized,
                    mode='lines+markers',
                    name=metric.replace('_', ' ').title()
                ))
            
            fig2.update_layout(
                title='Normalized Metrics Comparison',
                xaxis_title='Neighborhood',
                yaxis_title='Normalized Value (0-1)',
                xaxis_tickangle=-45
            )
            
            figures.append(fig2)
        
        if 'final_score' in df.columns and len(df) > 0:
            fig3 = px.histogram(
                df,
                x='final_score',
                nbins=30,
                title='Score Distribution',
                labels={'final_score': 'Final Score'}
            )
            figures.append(fig3)
        
        if 'median_income' in df.columns and 'competition_count' in df.columns and len(df) > 0:
            top_20 = df.head(20).copy()
            
            # Only add hover_data if neighborhood column exists
            hover_data_dict = {}
            if neighborhood_col:
                hover_data_dict = [neighborhood_col]
            
            fig4 = px.scatter(
                top_20,
                x='median_income',
                y='competition_count',
                size='final_score',
                color='final_score',
                hover_data=hover_data_dict if hover_data_dict else None,
                title='Income vs Competition (Top 20)',
                labels={
                    'median_income': 'Median Income ($)',
                    'competition_count': 'Competition Count'
                },
                color_continuous_scale='RdYlGn'
            )
            figures.append(fig4)
        
        return figures
    
    def save_charts(self, figures: List[go.Figure]) -> List[str]:
        """
        Save charts as HTML files
        """
        filepaths = []
        
        for i, fig in enumerate(figures):
            filename = f"chart_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(self.output_dir, filename)
            fig.write_html(filepath)
            filepaths.append(filepath)
        
        return filepaths


def save_csv(df: pd.DataFrame, filename: str, output_dir: str = "data/outputs") -> str:
    """
    Standalone function to save CSV
    """
    generator = OutputGenerator(output_dir)
    return generator.save_csv(df, filename)


def save_report(content: str, filename: str, output_dir: str = "data/outputs") -> str:
    """
    Standalone function to save report
    """
    generator = OutputGenerator(output_dir)
    return generator.save_report(content, filename)


def generate_charts(df: pd.DataFrame) -> List[go.Figure]:
    """
    Standalone function to generate charts
    """
    generator = OutputGenerator()
    return generator.generate_charts(df)