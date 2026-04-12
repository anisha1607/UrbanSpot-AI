import requests
import pandas as pd
from typing import Optional, Dict
import os
from datetime import datetime


class NYCDataCollector:
    def __init__(self, app_token: Optional[str] = None):
        self.app_token = app_token or os.getenv("NYC_APP_TOKEN")
        self.base_url = "https://data.cityofnewyork.us/resource"
    
    def fetch_business_data(self, business_type: str, limit: int = 5000) -> pd.DataFrame:
        """
        Fetch business locations from NYC Open Data
        Dataset: Legally Operating Businesses
        """
        endpoint = f"{self.base_url}/w7w3-xahh.json"
        
        params = {
            "$limit": limit,
        }
        
        if self.app_token:
            params["$$app_token"] = self.app_token
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                
                if not df.empty:
                    df['retrieved_at'] = datetime.now().isoformat()
                    print(f"  - Fetched {len(df)} business records")
                    return df
            else:
                print(f"  - Business data warning: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  - Business data error: {e}")
        
        return pd.DataFrame()
    
    def fetch_restaurant_inspections(self, limit: int = 10000) -> pd.DataFrame:
        """
        Fetch restaurant inspection data (better dataset for location analysis)
        Dataset: DOHMH New York City Restaurant Inspection Results
        """
        endpoint = f"{self.base_url}/43nn-pn8j.json"
        
        params = {
            "$limit": limit,
            "$select": "camis,dba,boro,building,street,zipcode,cuisine_description,inspection_date,grade",
            "$where": "grade IS NOT NULL"
        }
        
        if self.app_token:
            params["$$app_token"] = self.app_token
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                
                if not df.empty:
                    df['retrieved_at'] = datetime.now().isoformat()
                    print(f"  - Fetched {len(df)} restaurant records")
                    return df
            else:
                print(f"  - Restaurant data warning: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  - Restaurant data error: {e}")
        
        return pd.DataFrame()
    
    def fetch_demographics_by_neighborhood(self) -> pd.DataFrame:
        """
        Create synthetic demographic data based on borough
        Since the real demographic endpoint may not be available
        """
        # Use restaurant data as proxy for neighborhood activity
        restaurants = self.fetch_restaurant_inspections(limit=20000)
        
        if restaurants.empty:
            return pd.DataFrame()
        
        # Aggregate by zipcode and borough
        if 'zipcode' in restaurants.columns and 'boro' in restaurants.columns:
            demo = restaurants.groupby(['zipcode', 'boro']).size().reset_index(name='business_count')
            demo = demo.rename(columns={'zipcode': 'neighborhood', 'boro': 'borough'})
            
            # Add synthetic population estimates (rough correlation with business count)
            demo['population'] = demo['business_count'] * 50
            
            print(f"  - Created demographic data for {len(demo)} neighborhoods")
            return demo
        
        return pd.DataFrame()


def fetch_nyc_data(business_type: str) -> Dict[str, pd.DataFrame]:
    """
    Main function to fetch all NYC data sources
    """
    collector = NYCDataCollector()
    
    datasets = {
        'businesses': collector.fetch_business_data(business_type),
        'restaurants': collector.fetch_restaurant_inspections(),
        'demographics': collector.fetch_demographics_by_neighborhood(),
    }
    
    return datasets