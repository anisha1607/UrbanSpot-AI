import requests
import pandas as pd
from typing import Optional, List
import os


class CensusDataCollector:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CENSUS_API_KEY")
        self.base_url = "https://api.census.gov/data"
    
    def fetch_acs_data(self, year: int = 2021) -> pd.DataFrame:
        """
        Fetch American Community Survey data for NYC
        Variables:
        - B01003_001E: Total population
        - B19013_001E: Median household income
        - B25064_001E: Median gross rent
        """
        endpoint = f"{self.base_url}/{year}/acs/acs5"
        
        variables = [
            "B01003_001E",  # Total population
            "B19013_001E",  # Median household income
            "B25064_001E",  # Median gross rent
            "NAME"
        ]
        
        params = {
            "get": ",".join(variables),
            "for": "zip code tabulation area:*",
            "in": "state:36",  # New York state
            "key": self.api_key
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        data = response.json()
        df = pd.DataFrame(data[1:], columns=data[0])
        
        df = df.rename(columns={
            "B01003_001E": "population",
            "B19013_001E": "median_income",
            "B25064_001E": "median_rent",
            "NAME": "name",
            "zip code tabulation area": "zipcode"
        })
        
        for col in ['population', 'median_income', 'median_rent']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        nyc_zipcodes = self._get_nyc_zipcodes()
        df = df[df['zipcode'].isin(nyc_zipcodes)]
        
        return df
    
    def _get_nyc_zipcodes(self) -> List[str]:
        """
        Returns list of NYC zip codes by borough
        """
        return [
            # Manhattan
            '10001', '10002', '10003', '10004', '10005', '10006', '10007', '10009',
            '10010', '10011', '10012', '10013', '10014', '10016', '10017', '10018',
            '10019', '10020', '10021', '10022', '10023', '10024', '10025', '10026',
            '10027', '10028', '10029', '10030', '10031', '10032', '10033', '10034',
            '10035', '10036', '10037', '10038', '10039', '10040', '10044', '10065',
            '10069', '10075', '10103', '10110', '10111', '10112', '10115', '10119',
            '10128', '10152', '10153', '10154', '10162', '10165', '10167', '10168',
            '10169', '10170', '10171', '10172', '10173', '10174', '10177', '10199',
            '10271', '10278', '10279', '10280', '10282',
            # Brooklyn
            '11201', '11203', '11204', '11205', '11206', '11207', '11208', '11209',
            '11210', '11211', '11212', '11213', '11214', '11215', '11216', '11217',
            '11218', '11219', '11220', '11221', '11222', '11223', '11224', '11225',
            '11226', '11228', '11229', '11230', '11231', '11232', '11233', '11234',
            '11235', '11236', '11237', '11238', '11239', '11241', '11242', '11243',
            '11249', '11252', '11256',
            # Queens
            '11004', '11005', '11101', '11102', '11103', '11104', '11105', '11106',
            '11109', '11351', '11354', '11355', '11356', '11357', '11358', '11359',
            '11360', '11361', '11362', '11363', '11364', '11365', '11366', '11367',
            '11368', '11369', '11370', '11371', '11372', '11373', '11374', '11375',
            '11377', '11378', '11379', '11385', '11411', '11412', '11413', '11414',
            '11415', '11416', '11417', '11418', '11419', '11420', '11421', '11422',
            '11423', '11426', '11427', '11428', '11429', '11430', '11432', '11433',
            '11434', '11435', '11436', '11691', '11692', '11693', '11694', '11697',
            # Bronx
            '10451', '10452', '10453', '10454', '10455', '10456', '10457', '10458',
            '10459', '10460', '10461', '10462', '10463', '10464', '10465', '10466',
            '10467', '10468', '10469', '10470', '10471', '10472', '10473', '10474',
            '10475',
            # Staten Island
            '10301', '10302', '10303', '10304', '10305', '10306', '10307', '10308',
            '10309', '10310', '10311', '10312', '10313', '10314'
        ]


def fetch_census_data() -> pd.DataFrame:
    """
    Main function to fetch Census data
    """
    collector = CensusDataCollector()
    return collector.fetch_acs_data()
