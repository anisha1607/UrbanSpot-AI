import sys
sys.path.append('/home/claude/business-location-advisor')

from typing import Dict, Any, List
import pandas as pd
from tools.nyc_data import fetch_nyc_data
from tools.census_data import fetch_census_data
from tools.mta_data import fetch_mta_data


class DataCollectorAgent:
    """
    Fetches data from APIs and normalizes datasets
    """
    
    def __init__(self):
        self.collected_data = {}
    
    def collect(self, plan: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """
        Collect data based on analysis plan
        """
        datasets = {}
        data_sources = plan.get('data_sources', [])
        business_type = plan.get('business_type', 'general')
        
        print(f"Collecting data from {len(data_sources)} sources for business type: {business_type}...")
        
        # Fetch NYC business data (restaurants, retail, gyms, salons, etc.)
        # The fetch_nyc_data function handles different business types dynamically
        if any(source in ['nyc_businesses', 'restaurants', 'nyc_open_data', 'businesses'] for source in data_sources):
            print(f"Fetching NYC Open Data for {business_type}...")
            try:
                nyc_data = fetch_nyc_data(business_type)
                datasets.update(nyc_data)
                
                # Show what was fetched dynamically
                for key, df in nyc_data.items():
                    if not df.empty:
                        print(f"  - {key.capitalize()}: {len(df)} records")
                    
            except Exception as e:
                print(f"  - Error fetching NYC data: {e}")
                # Add empty dataframes as fallback
                datasets['businesses'] = pd.DataFrame()
                if business_type in ['restaurant', 'coffee_shop', 'cafe']:
                    datasets['restaurants'] = pd.DataFrame()
        
        # Fetch Census data (population, income, rent by zip code)
        if 'census' in data_sources:
            print("Fetching Census data...")
            try:
                census_data = fetch_census_data()
                datasets['census'] = census_data
                print(f"  - Census: {len(census_data)} records")
            except Exception as e:
                print(f"  - Error fetching Census data: {e}")
                datasets['census'] = pd.DataFrame()
        
        # Fetch MTA data (subway ridership for foot traffic proxy)
        if 'mta' in data_sources:
            print("Fetching MTA data...")
            try:
                mta_data = fetch_mta_data()
                datasets['mta'] = mta_data
                print(f"  - MTA: {len(mta_data)} records")
            except Exception as e:
                print(f"  - Error fetching MTA data: {e}")
                datasets['mta'] = pd.DataFrame()
        
        self.collected_data = datasets
        
        print(f"\n✓ Data collection complete: {len(datasets)} datasets")
        return datasets
    
    def normalize_datasets(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Normalize and clean collected datasets
        """
        normalized = {}
        
        for name, df in datasets.items():
            if df.empty:
                normalized[name] = df
                continue
            
            clean_df = df.copy()
            
            # Normalize column names
            clean_df.columns = clean_df.columns.str.lower().str.strip()
            
            # Clean string columns
            for col in clean_df.columns:
                if clean_df[col].dtype == 'object':
                    clean_df[col] = clean_df[col].str.strip()
            
            normalized[name] = clean_df
        
        return normalized
    
    def get_data_summary(self) -> List[Dict[str, Any]]:
        """
        Generate summary of collected datasets
        """
        summary = []
        
        for name, df in self.collected_data.items():
            if not df.empty:
                summary.append({
                    'source': name,
                    'rows': len(df),
                    'columns': list(df.columns),
                    'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
                })
        
        return summary


def collect_data(plan: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """
    Standalone function to collect data
    """
    collector = DataCollectorAgent()
    datasets = collector.collect(plan)
    return collector.normalize_datasets(datasets)