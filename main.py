from data_formatter import DataFormatter
from predictor_gui import PredictorGui


if __name__ == "__main__":
    df = DataFormatter()
    df.import_csv_data("cars_dataset/cars.csv")

    PredictorGui(df, "trained_models/price_predictor.pkl")
