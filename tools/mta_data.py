import requests
import pandas as pd
from typing import Optional
import os


class MTADataCollector:
    def __init__(self):
        self.base_url = "https://data.ny.gov/resource"
    
    def fetch_subway_ridership(self, limit: int = 50000) -> pd.DataFrame:
        """
        Fetch MTA subway station ridership data
        Dataset: MTA Subway Hourly Ridership
        """
        endpoint = f"{self.base_url}/wujg-7c2s.json"
        
        params = {
            "$limit": limit,
            "$order": "transit_timestamp DESC"
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            df = pd.DataFrame(response.json())
            return df
        except Exception as e:
            print(f"Error fetching subway ridership: {e}")
            return pd.DataFrame()
    
    def fetch_turnstile_data(self, limit: int = 100000) -> pd.DataFrame:
        """
        Fetch MTA turnstile data for foot traffic analysis
        This provides entry/exit data per station
        """
        url = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_231209.txt"
        
        try:
            df = pd.read_csv(url)
            df.columns = df.columns.str.strip()
            
            df['ENTRIES'] = pd.to_numeric(df['ENTRIES'], errors='coerce')
            df['EXITS'] = pd.to_numeric(df['EXITS'], errors='coerce')
            
            return df
        except Exception as e:
            print(f"Error fetching turnstile data: {e}")
            return pd.DataFrame()
    
    def aggregate_by_station(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate turnstile data by station to get total traffic
        """
        if df.empty:
            return pd.DataFrame()
        
        station_traffic = df.groupby(['STATION']).agg({
            'ENTRIES': 'sum',
            'EXITS': 'sum'
        }).reset_index()
        
        station_traffic['TOTAL_TRAFFIC'] = (
            station_traffic['ENTRIES'] + station_traffic['EXITS']
        )
        
        return station_traffic.sort_values('TOTAL_TRAFFIC', ascending=False)


def fetch_mta_data() -> pd.DataFrame:
    """
    Main function to fetch MTA data
    """
    collector = MTADataCollector()
    
    ridership = collector.fetch_subway_ridership()
    
    if not ridership.empty:
        return ridership
    
    turnstile = collector.fetch_turnstile_data()
    
    if not turnstile.empty:
        return collector.aggregate_by_station(turnstile)
    
    return pd.DataFrame()
