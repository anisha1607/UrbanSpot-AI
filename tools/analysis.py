import pandas as pd
import duckdb
from typing import Dict, List, Tuple
import numpy as np


class DataAnalyzer:
    def __init__(self):
        self.con = duckdb.connect(database=':memory:')
        # Real NYC residential zip codes by borough
        self.nyc_residential_zips = {
            'MANHATTAN': ['10001', '10002', '10003', '10009', '10010', '10011', '10012', '10013', '10014', 
                         '10016', '10017', '10018', '10019', '10021', '10022', '10023', '10024', '10025', 
                         '10026', '10027', '10028', '10029', '10030', '10031', '10032', '10033', '10034', 
                         '10035', '10036', '10037', '10038', '10039', '10040', '10128', '10280', '10282'],
            'BROOKLYN': ['11201', '11203', '11204', '11205', '11206', '11207', '11208', '11209', '11210', 
                        '11211', '11212', '11213', '11214', '11215', '11216', '11217', '11218', '11219', 
                        '11220', '11221', '11222', '11223', '11224', '11225', '11226', '11228', '11229', 
                        '11230', '11231', '11232', '11233', '11234', '11235', '11236', '11237', '11238', '11239'],
            'QUEENS': ['11101', '11102', '11103', '11104', '11105', '11106', '11354', '11355', '11356', 
                      '11357', '11358', '11359', '11360', '11361', '11362', '11363', '11364', '11365', 
                      '11366', '11367', '11368', '11369', '11370', '11372', '11373', '11374', '11375', 
                      '11377', '11378', '11379', '11385', '11411', '11412', '11413', '11414', '11415', 
                      '11416', '11417', '11418', '11419', '11420', '11421', '11422', '11423', '11426', 
                      '11427', '11428', '11429', '11430', '11432', '11433', '11434', '11435', '11436'],
            'BRONX': ['10451', '10452', '10453', '10454', '10455', '10456', '10457', '10458', '10459', 
                     '10460', '10461', '10462', '10463', '10464', '10465', '10466', '10467', '10468', 
                     '10469', '10470', '10471', '10472', '10473', '10474', '10475'],
            'STATEN ISLAND': ['10301', '10302', '10303', '10304', '10305', '10306', '10307', '10308', 
                             '10309', '10310', '10311', '10312', '10313', '10314']
        }
        # Flatten to a set for easy lookup
        self.all_residential_zips = set()
        for zips in self.nyc_residential_zips.values():
            self.all_residential_zips.update(zips)
    
    def merge_datasets(
        self,
        datasets: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Merge all datasets into a unified neighborhood-level table
        """
        merged = pd.DataFrame()
        
        # Start with restaurant data as the base (most reliable)
        if 'restaurants' in datasets and not datasets['restaurants'].empty:
            rest = datasets['restaurants']
            
            if 'boro' in rest.columns and 'zipcode' in rest.columns:
                # Clean and standardize zip codes
                rest['zipcode'] = rest['zipcode'].astype(str).str.strip().str[:5]
                rest['boro'] = rest['boro'].astype(str).str.upper().str.strip()
                
                # Filter to only NYC residential zip codes
                rest = rest[rest['zipcode'].isin(self.all_residential_zips)]
                
                if rest.empty:
                    print("  - Warning: No residential zip codes found in restaurant data")
                    return pd.DataFrame()
                
                # Count restaurants by zipcode and borough
                competition = rest.groupby(['zipcode', 'boro']).size().reset_index(name='competition_count')
                merged = competition.copy()
                print(f"  - Base data: {len(merged)} residential neighborhoods from restaurants")
        
        # Add Census data (income, rent, population)
        if 'census' in datasets and not datasets['census'].empty:
            census = datasets['census'].copy()
            
            # Ensure zipcode is string for merging
            if 'zipcode' in census.columns:
                census['zipcode'] = census['zipcode'].astype(str).str.strip().str[:5]
                
                # Filter to only NYC residential zip codes
                census = census[census['zipcode'].isin(self.all_residential_zips)]
                
                if not merged.empty:
                    merged['zipcode'] = merged['zipcode'].astype(str).str.strip()
                    
                    # Merge on zipcode
                    merged = merged.merge(
                        census[['zipcode', 'population', 'median_income', 'median_rent']],
                        on='zipcode',
                        how='left'
                    )
                    print(f"  - Added Census data: {merged['median_income'].notna().sum()} neighborhoods with income data")
                else:
                    # Use census as base if no restaurant data
                    merged = census[['zipcode', 'population', 'median_income', 'median_rent']].copy()
                    merged['competition_count'] = 0
                    merged['boro'] = 'Unknown'
        
        if merged.empty:
            print("  - Warning: No data could be merged")
            return pd.DataFrame()
        
        # Create neighborhood identifier
        if 'zipcode' in merged.columns and 'boro' in merged.columns:
            merged['neighborhood'] = merged['boro'].str.title() + ' - ' + merged['zipcode'].astype(str)
        elif 'zipcode' in merged.columns:
            merged['neighborhood'] = merged['zipcode'].astype(str)
        
        # Fill missing values with zeros
        for col in ['population', 'median_income', 'median_rent', 'competition_count']:
            if col in merged.columns:
                merged[col] = pd.to_numeric(merged[col], errors='coerce').fillna(0)
            elif col == 'population':
                # If no population column, estimate from competition count
                if 'competition_count' in merged.columns:
                    merged['population'] = merged['competition_count'] * 100
                    print("  - Note: Using estimated population from business density")
                else:
                    merged['population'] = 0
        
        # Log what we have before filtering
        print(f"  - Data before filtering: {len(merged)} neighborhoods")
        if 'median_income' in merged.columns:
            print(f"  - Income range: ${merged['median_income'].min():.0f} - ${merged['median_income'].max():.0f}")
        if 'population' in merged.columns:
            print(f"  - Population range: {merged['population'].min():.0f} - {merged['population'].max():.0f}")
        if 'competition_count' in merged.columns:
            print(f"  - Competition range: {merged['competition_count'].min():.0f} - {merged['competition_count'].max():.0f}")
        
        # Light filtering - just remove completely empty rows
        before_filter = len(merged)
        merged = merged[
            (merged.get('competition_count', 0) > 0) |
            (merged.get('median_income', 0) > 0) |
            (merged.get('population', 0) > 0)
        ]
        
        print(f"  - Filtered {before_filter - len(merged)} completely empty neighborhoods")
        print(f"  - Final merged dataset: {len(merged)} valid neighborhoods")
        
        return merged
    
    def compute_scores(
        self,
        df: pd.DataFrame,
        weights: Dict[str, float]
    ) -> pd.DataFrame:
        """
        Compute final scores for each neighborhood
        Score = w1*Demand + w2*FootTraffic + w3*Income - w4*Competition - w5*Rent
        """
        if df.empty:
            print("  - Warning: Empty dataframe, cannot compute scores")
            return df
        
        result = df.copy()
        
        # Ensure all required columns exist (create with zeros if missing)
        for col in ['population', 'median_income', 'competition_count', 'median_rent']:
            if col not in result.columns:
                result[col] = 0
                print(f"  - Warning: {col} column missing, using zeros")
            else:
                result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0)
        
        # Normalize metrics (only if they have non-zero values)
        result['population_norm'] = self._normalize(result['population']) if result['population'].max() > 0 else 0
        result['income_norm'] = self._normalize(result['median_income']) if result['median_income'].max() > 0 else 0
        result['competition_norm'] = self._normalize(result['competition_count']) if result['competition_count'].max() > 0 else 0
        result['rent_norm'] = self._normalize(result['median_rent']) if result['median_rent'].max() > 0 else 0
        
        result['demand_score'] = result['population_norm']
        result['foot_traffic_score'] = result['population_norm'] * 0.5
        
        result['final_score'] = (
            weights.get('demand', 0.25) * result['demand_score'] +
            weights.get('foot_traffic', 0.20) * result['foot_traffic_score'] +
            weights.get('income', 0.20) * result['income_norm'] -
            weights.get('competition', 0.20) * result['competition_norm'] -
            weights.get('rent', 0.15) * result['rent_norm']
        )
        
        result = result.sort_values('final_score', ascending=False)
        
        print(f"  - Scored {len(result)} neighborhoods")
        if len(result) > 0:
            print(f"  - Top score: {result['final_score'].max():.3f}, Bottom score: {result['final_score'].min():.3f}")
        
        return result
    
    def _normalize(self, series: pd.Series) -> pd.Series:
        """
        Min-max normalization
        """
        min_val = series.min()
        max_val = series.max()
        
        if max_val == min_val or max_val == 0:
            return pd.Series([0.5] * len(series), index=series.index)
        
        return (series - min_val) / (max_val - min_val)
    
    def summarize_results(self, df: pd.DataFrame, top_n: int = 10) -> Dict:
        """
        Generate summary statistics for top neighborhoods
        """
        if df.empty:
            return {
                'total_neighborhoods': 0,
                'top_neighborhoods': [],
                'avg_score': 0,
                'score_std': 0,
                'metrics': {}
            }
        
        top_neighborhoods = df.head(top_n)
        
        summary = {
            'total_neighborhoods': len(df),
            'top_neighborhoods': top_neighborhoods.to_dict('records'),
            'avg_score': float(df['final_score'].mean()) if 'final_score' in df.columns else 0,
            'score_std': float(df['final_score'].std()) if 'final_score' in df.columns else 0,
            'metrics': {
                'avg_competition': float(df['competition_count'].mean()) if 'competition_count' in df.columns else 0,
                'avg_income': float(df['median_income'].mean()) if 'median_income' in df.columns else 0,
                'avg_rent': float(df['median_rent'].mean()) if 'median_rent' in df.columns else 0,
            }
        }
        
        return summary


def merge_datasets(datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Standalone function to merge datasets
    """
    analyzer = DataAnalyzer()
    return analyzer.merge_datasets(datasets)


def compute_scores(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    """
    Standalone function to compute scores
    """
    analyzer = DataAnalyzer()
    return analyzer.compute_scores(df, weights)


def summarize_results(df: pd.DataFrame, top_n: int = 10) -> Dict:
    """
    Standalone function to summarize results
    """
    analyzer = DataAnalyzer()
    return analyzer.summarize_results(df, top_n)