import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from matplotlib.ticker import MaxNLocator


class PictureGenerator:
    @staticmethod
    def generate_histogram_picture(data: pd.DataFrame, title: str):
        plt.figure(figsize=(10, 6), dpi=300)
        plt.bar(data.index, data, color="skyblue", edgecolor="black", alpha=0.8)

        plt.title(title, fontsize=16)
        plt.xlabel("Язык", fontsize=14)
        plt.ylabel("Количество", fontsize=14)

        plt.xticks(rotation=45, ha="right")  # Поворот подписей для удобства чтения

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()  # Автоматическая подстройка элементов

        plt.savefig(f"hist_{title}.png")

    @staticmethod
    def generate_pie_picture(data: pd.DataFrame, title: str):
        fig, ax = plt.subplots(
            figsize=(20, 15), subplot_kw=dict(aspect="equal"), dpi=300
        )

        wedges, texts, autotexts = ax.pie(
            data,
            autopct=lambda pct: f"{pct:.1f}%",
            textprops=dict(color="w", rotation=0),
            colors=plt.cm.Dark2.colors,
            startangle=45,
        )

        ax.legend(
            wedges,
            data.index,
            title="Языки",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=24,
            title_fontsize=28,
        )

        plt.setp(autotexts, size=18, weight=700)
        ax.set_title(title, fontsize=46)

        plt.savefig(f"pie_{title}.png")

    @staticmethod
    def generate_picture(data: pd.DataFrame, title: str):
        langs = data.index.get_level_values(0).unique()

        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=10))

        for lang in langs:
            lang_data = data.loc[lang]
            plt.plot(lang_data.index[:-1], lang_data[:-1], label=lang)

        plt.title(title, fontsize=14)
        plt.xlabel("Время", fontsize=12)
        plt.ylabel("Количество", fontsize=12)
        plt.legend(title="Языки", fontsize=12)
        plt.grid(True)

        plt.savefig(f"line_{title}.png")


def func(pct, allvals):
    absolute = int(pct / 100.0 * np.sum(allvals))
    return "{:.1f}% ({:d} )".format(pct, absolute)
