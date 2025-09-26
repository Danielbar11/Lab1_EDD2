import pandas as pd
import os

class DataLoader:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None

    def load_data(self):
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"No se encontró el archivo: {self.csv_path}")

        self.df = pd.read_csv(self.csv_path)

        years = [f'F{year}' for year in range(1961, 2023)]

        self.df['average'] = self.df[years].mean(axis=1).round(4)

        return self.df

    def get_country_data(self, iso3):
        if self.df is None:
            raise ValueError("Ha ocurrido un error")
        country_row = self.df[self.df['ISO3'] == iso3]
        if country_row.empty:
            return None
        return country_row.to_dict(orient='records')[0]

    def get_all_countries(self):
        if self.df is None:
            raise ValueError("Ha ocurrido un error")
        return self.df.to_dict(orient='records')