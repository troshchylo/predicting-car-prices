import csv
import json


class DataFormatter:
    def __init__(self):
        self.data = set()
        self.euro_rate = 4.5

    def get_data(self):
        return list(self.data)

    def import_csv_data(self, path):
        with open(path, newline="") as file:
            reader = csv.reader(file, delimiter=",", quotechar="|")

            for row in reader:
                if self.is_valid_row(row):
                    self.format_row(row)
                    self.data.add(tuple(row))

    def format_row(self, row):
        # rok produkcji
        row[2] = int(row[2])
        # przebieg
        row[3] = int("".join(row[3].split(" ")[:-1]))
        # pojemnosc skokowa
        row[4] = int("".join(row[4].split(" ")[:-1]))
        # cena
        row[6] = self.get_pln_price(row[6])

    def get_pln_price(self, raw_price):
        *amount, currency = raw_price.split(" ")
        amount = int("".join(amount))

        if currency == "PLN":
            return amount
        elif currency == "EUR":
            return int(amount * self.euro_rate)

    def is_valid_row(self, row):
        return (
            "km" in row[3]
            and "cm3" in row[4]
            and row[5]
            in [
                "Benzyna",
                "Benzyna+CNG",
                "Benzyna+LPG",
                "Diesel",
                "Elektryczny",
                "Hybryda",
            ]
        )

    def brand_models_json(self, path):
        bm_dict = {}

        for brand, model, _, _, _, _, _ in self.data:
            if brand not in bm_dict.keys():
                bm_dict[brand] = set()
            bm_dict[brand].add(model)

        for brand, models in bm_dict.items():
            bm_dict[brand] = list(models)

        with open(path, "w") as outfile:
            json.dump(bm_dict, outfile, indent=4)
