import tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter
from data_formatter import DataFormatter
from price_predictor import PricePredictor
import json
import pandas as pd
import matplotlib.ticker as ticker
import numpy as np


class PredictorGui:
    window_size = "1000x600"
    title = "Car price predictor"
    labelbg = "#3F8597"
    price_color = "#3F5497"
    error_color = "#C64F4F"
    labels = [
        "Marka pojazdu",
        "Model pojazdu",
        "Rok produkcji",
        "Przebieg",
        "Pojemność skokowa",
        "Rodzaj paliwa",
    ]
    fuel_types = [
        "Benzyna",
        "Benzyna+CNG",
        "Benzyna+LPG",
        "Diesel",
        "Elektryczny",
        "Hybryda",
    ]
    brand_models_path = "cars_dataset/brand_models.json"

    def __init__(self, df: DataFormatter, model_path):
        self.dataf = df
        self.pd_data = pd.DataFrame(df.get_data(), columns=self.labels + ["Cena"])
        self.ppred = PricePredictor()
        self.ppred.import_cars_data(df)
        self.ppred.load_model(model_path)
        self.entries = []

        with open(self.brand_models_path, "r") as file:
            self.brand_models = json.load(file)

        self.init_window()

    def init_window(self):
        self.root_tk = customtkinter.CTk()
        self.root_tk.geometry(self.window_size)
        self.root_tk.resizable(False, False)
        self.root_tk.title(self.title)

        for ind, text in enumerate(self.labels):
            label = customtkinter.CTkLabel(
                master=self.root_tk,
                text=text,
                width=150,
                height=25,
                bg_color=self.labelbg,
            )
            label.place(
                # dziele przez 3 po to zeby umiescic to w 2 kolumnach
                relx=0.15 + 0.5 * (ind // 3),
                rely=0.05 + 0.1 * (ind % 3),
                anchor=tkinter.CENTER,
            )

            entry = customtkinter.CTkEntry(master=self.root_tk, width=150, height=25)
            entry.place(
                relx=0.35 + 0.5 * (ind // 3),
                rely=0.05 + 0.1 * (ind % 3),
                anchor=tkinter.CENTER,
            )

            self.entries.append(entry)

        button = customtkinter.CTkButton(
            master=self.root_tk,
            text="Przewidź cenę",
            command=self.button_event,
            width=350,
            height=25,
            border_width=0,
            corner_radius=0,
            fg_color=self.price_color,
        )
        button.place(relx=0.75, rely=0.35, anchor=tkinter.CENTER)

        label = customtkinter.CTkLabel(
            master=self.root_tk,
            text="Proponowana cena: ",
            width=150,
            height=25,
            bg_color=self.price_color,
        )
        label.place(relx=0.15, rely=0.35, anchor=tkinter.CENTER)

        self.predicted_price_label = customtkinter.CTkLabel(
            master=self.root_tk,
            text="- PLN",
            width=150,
            height=25,
            bg_color=self.price_color,
        )
        self.predicted_price_label.place(relx=0.35, rely=0.35, anchor=tkinter.CENTER)

        self.error_label = customtkinter.CTkLabel(
            master=self.root_tk,
            text="",
            width=100,
            height=25,
            bg_color=self.error_color,
        )

        self.root_tk.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.root_tk.mainloop()

    def on_window_close(self):
        plt.close("all")
        self.root_tk.destroy()

    def button_event(self):
        car_features = []

        self.error_label.place_forget()

        for entry in self.entries:
            car_features.append(entry.get())

        try:
            car_features[2] = int(car_features[2])
            car_features[3] = int(car_features[3])
            car_features[4] = int(car_features[4])
        except ValueError:
            self.place_error("Błąd odczytu")
            return

        car_features[0] = car_features[0].lower().replace(" ", "-")
        car_features[1] = car_features[1].lower().replace(" ", "-")
        car_features[5] = car_features[5].lower().capitalize()

        if (
            car_features[0] not in self.brand_models.keys()
            or car_features[1] not in self.brand_models[car_features[0]]
            or car_features[5] not in self.fuel_types
            or not all(value > 0 for value in car_features[2:5])
        ):
            self.place_error("Błąd odczytu")
            return

        predicted_price = self.ppred.predict_price(car_features)[0]
        self.predicted_price_label.configure(text=f"{predicted_price:,.2f} PLN")

        self.draw_analysis(car_features[0], car_features[1])

    def place_error(self, text):
        self.error_label.configure(text=text)
        self.error_label.place(relx=0.5, rely=0.35, anchor=tkinter.CENTER)

    def draw_analysis(self, brand, model):
        car_data = self.pd_data.loc[
            (self.pd_data["Marka pojazdu"] == brand)
            & (self.pd_data["Model pojazdu"] == model)
        ]

        car_mileage_price = (
            car_data.loc[car_data["Przebieg"] < 400000]
            .groupby("Przebieg")["Cena"]
            .mean()
        )
        car_mileage_price = car_mileage_price.sort_index()

        car_year_price = car_data.groupby("Rok produkcji")["Cena"].mean()
        car_year_price = car_year_price.sort_index()

        self.plot_analysis(
            car_mileage_price.index,
            car_mileage_price.values,
            "Przebieg, tys",
            "Cena, tys",
            "Cena w zależności od przebiegu",
            0.3,
            0.7,
            (5.8, 3.4),
            lambda x, _: "{:.0f}".format(x / 1000),
        )

        self.plot_analysis(
            car_year_price.index,
            car_year_price.values,
            "Rok produkcji",
            "Cena, tys",
            "Cena w zależności od roku produkcji",
            0.8,
            0.7,
            (3.9, 3.4),
            lambda x, _: f"{x:.0f}",
        )

    def plot_analysis(
        self, x_data, y_data, x_label, y_label, title, relx, rely, figsize, xaxis_format
    ):
        figure, ax = plt.subplots(figsize=figsize)
        ax.plot(x_data, y_data)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        ax.grid(True)
        ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda y, _: "{:.0f}".format(y / 1000))
        )
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(xaxis_format))

        plt.tight_layout()

        xticks = plt.xticks()[0]
        xticks = np.linspace(max(0, xticks[0]), xticks[-1], num=5)
        plt.xticks(xticks)

        canvas = FigureCanvasTkAgg(figure, master=self.root_tk)
        canvas.draw()
        canvas.get_tk_widget().place(relx=relx, rely=rely, anchor=tkinter.CENTER)
