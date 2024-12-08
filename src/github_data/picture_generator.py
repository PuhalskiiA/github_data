import numpy as np
import pandas as pd

from matplotlib import pyplot as plt


class PictureGenerator:
    @staticmethod
    def generate_histogram_picture(
        data: pd.DataFrame, title: str, xlabel: str, ylabel: str
    ):
        plt.figure(figsize=(10, 6))
        plt.bar(data.index, data, color="skyblue", edgecolor="black", alpha=0.8)

        plt.title(title, fontsize=16)
        plt.xlabel(xlabel, fontsize=14)
        plt.ylabel(ylabel, fontsize=14)

        plt.xticks(rotation=45, ha="right")  # Поворот подписей для удобства чтения

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()  # Автоматическая подстройка элементов

        plt.savefig(f"{title}.png")

    @staticmethod
    def generate_pie_picture(data: pd.DataFrame, title: str, item_name: str):
        fig, ax = plt.subplots(
            figsize=(20, 15), subplot_kw=dict(aspect="equal"), dpi=80
        )

        explode = [0] * len(data)

        wedges, texts, autotexts = ax.pie(
            data,
            autopct=lambda pct: func(pct, data),
            textprops=dict(color="w", rotation=0),
            colors=plt.cm.Dark2.colors,
            startangle=45,
            explode=explode,
        )

        ax.legend(
            wedges,
            data.index,
            title=item_name,
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=24,
            title_fontsize=28,
        )

        plt.setp(autotexts, size=18, weight=700)
        ax.set_title(title, fontsize=46)

        plt.savefig(f"{title}.png")

    @staticmethod
    def generate_picture(data: pd.DataFrame, title: str, xlabel: str, ylabel: str):
        langs = data.index.get_level_values(0).unique()

        # columns = data.columns.tolist()
        # group_col = columns[
        #     0
        # ]  # Предполагается, что первый столбец — это группирующий (категории)
        # x_col = columns[1]  # Второй столбец — это ось X
        # y_col = columns[2]  # Третий столбец — это ось Y

        plt.figure(figsize=(10, 6), dpi=80)

        # grouped = data.groupby(group_col)
        for lang in langs:
            lang_data = data.loc[lang]
            plt.plot(lang_data.index, lang_data, label=lang)

        plt.title(title, fontsize=14)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        # plt.legend(title=group_col, fontsize=12)
        plt.grid(True)

        plt.savefig(f"{title}.png")


def func(pct, allvals):
    absolute = int(pct / 100.0 * np.sum(allvals))
    return "{:.1f}% ({:d} )".format(pct, absolute)
