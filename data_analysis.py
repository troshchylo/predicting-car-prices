import pandas as pd
import matplotlib.pyplot as plt
from data_formatter import DataFormatter
from matplotlib import ticker
import numpy as np


class DataAnalyzer:
    columns = [
        'Marka pojazdu',
        'Model pojazdu',
        'Rok produkcji',
        'Przebieg',
        'Pojemnosc skokowa',
        'Rodzaj paliwa',
        'Cena']

    def __init__(self, path: str):
        self.df = DataFormatter()
        self.df.import_csv_data(path)
        self.dataset = pd.DataFrame(self.df.get_data(), columns=self.columns)

    def __init__(self, df: DataFormatter):
        self.df = df
        self.dataset = pd.DataFrame(self.df.get_data(), columns=self.columns)

    def brand_prices(self):
        grouped_data = self.dataset.groupby('Marka pojazdu')['Cena'].mean()
        sorted_data = grouped_data.sort_values(ascending=False)

        plt.figure(figsize=(18, 8))
        sorted_data.plot(kind='bar')

        plt.xlabel('Brand')
        plt.ylabel('Average Price')
        plt.title('Average Price by Brand')

        plt.xticks(rotation=65, ha='right')
        plt.subplots_adjust(bottom=0.2)

        formatter = ticker.StrMethodFormatter('{x:,.0f}')
        plt.gca().yaxis.set_major_formatter(formatter)

        plt.show()

    def brand_counts(self):
        brand_counts = self.dataset['Marka pojazdu'].value_counts()
        brand_counts.sort_values(ascending=False)

        plt.figure(figsize=(18, 8))
        brand_counts.plot(kind='bar')

        plt.xlabel('Brand')
        plt.ylabel('Quantity')
        plt.title('Number of cars of each brand')

        plt.xticks(rotation=65, ha='right')
        plt.subplots_adjust(bottom=0.2)

        plt.show()

    def fuel_type_counts(self):
        fuel_counts = self.dataset['Rodzaj paliwa'].value_counts()
        fuel_counts.sort_values(ascending=False)

        plt.figure(figsize=(10, 8))
        fuel_counts.plot(kind='bar')

        plt.xlabel('Fuel type')
        plt.ylabel('Quantity')
        plt.title('Number of fuel types')
        plt.xticks(rotation=0)

        plt.show()

    def avg_price_by_year(self):
        grouped_data = self.dataset.groupby('Rok produkcji')['Cena'].mean()
        sorted_data = grouped_data.sort_index()

        plt.figure(figsize=(18, 8))
        sorted_data.plot(kind='bar')

        plt.xlabel('Year of production')
        plt.ylabel('Average Price')
        plt.title('Average Price by year of production')

        x_values = np.arange(0, len(sorted_data), 10)
        plt.xticks(x_values, rotation=0)

        formatter = ticker.StrMethodFormatter('{x:,.0f}')
        plt.gca().yaxis.set_major_formatter(formatter)

        plt.show()
