import pandas as pd
import joblib
from sklearn.tree import DecisionTreeRegressor
from data_formatter import DataFormatter


class PricePredictor:
    columns = [
        "Marka pojazdu",
        "Model pojazdu",
        "Rok produkcji",
        "Przebieg",
        "Pojemnosc skokowa",
        "Rodzaj paliwa",
        "Cena",
    ]

    def __init__(self):
        self.model = DecisionTreeRegressor()
        self.cars_features = pd.DataFrame()
        self.cars_prices = []

    def import_cars_data(self, df: DataFormatter):
        data = df.get_data()

        df_data = pd.DataFrame(data, columns=self.columns)

        self.cars_features = df_data.drop("Cena", axis=1)
        self.cars_prices = df_data["Cena"]
        self.cars_features = pd.get_dummies(self.cars_features)

    def fit_model(self):
        self.model.fit(self.cars_features, self.cars_prices)

    def predict_price(self, car_features):
        car_features_dict = {
            "Marka pojazdu": [car_features[0]],
            "Model pojazdu": [car_features[1]],
            "Rok produkcji": [car_features[2]],
            "Przebieg": [car_features[3]],
            "Pojemnosc skokowa": [car_features[4]],
            "Rodzaj paliwa": [car_features[5]],
        }

        car_features_df = pd.DataFrame(car_features_dict)
        car_features_encoded = pd.get_dummies(car_features_df)
        car_features_encoded = car_features_encoded.reindex(
            columns=self.cars_features.columns, fill_value=0
        )

        return self.model.predict(car_features_encoded)

    def save_model(self, path):
        joblib.dump(self.model, path)

    def load_model(self, path):
        self.model = joblib.load(path)
