from tools.analysis import DataAnalyzer
import pandas as pd

analyzer = DataAnalyzer()
df = pd.DataFrame({
    'population': [1000, 2000, 3000],
    'median_income': [50000, 100000, 150000],
    'competition_count': [10, 20, 30],
    'median_rent': [1000, 2000, 3000],
    'local_foot_traffic': [500, 1500, 2500],
    'transit_stations_count': [1, 2, 3],
    'neighborhood': ['N1', 'N2', 'N3']
})

weights = {'demand': 0.25, 'foot_traffic': 0.20, 'income': 0.20, 'competition': 0.20, 'rent': 0.15}
scored = analyzer.compute_scores(df, weights)
print(scored[['neighborhood', 'final_score']])
