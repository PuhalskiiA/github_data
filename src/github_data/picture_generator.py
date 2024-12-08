import numpy as np

from matplotlib import pyplot as plt


class PictureGenerator:
    @staticmethod
    def generate_histogram_picture(data: list, x_item: str, y_item: str, title: str, xlabel: str, ylabel: str):
        languages = [item[x_item] for item in data]
        counts = [item[y_item] for item in data]

        plt.figure(figsize=(10, 6))
        plt.bar(languages, counts, color='skyblue', edgecolor='black', alpha=0.8)

        plt.title(title, fontsize=16)
        plt.xlabel(xlabel, fontsize=14)
        plt.ylabel(ylabel, fontsize=14)

        plt.xticks(rotation=45, ha='right')  # Поворот подписей для удобства чтения

        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()  # Автоматическая подстройка элементов

        plt.show()

    @staticmethod
    def generate_pie_picture(data: list, title: str, item_name: str):
        fig, ax = plt.subplots(figsize=(20, 15), subplot_kw=dict(aspect="equal"), dpi=80)

        languages = [item["name"] for item in data]
        counts = [item["count"] for item in data]
        explode = [0] * (len(languages) - 1) + [0.1]

        wedges, texts, autotexts = ax.pie(counts,
                                          autopct=lambda pct: func(pct, counts),
                                          textprops=dict(color="w", rotation=0),
                                          colors=plt.cm.Dark2.colors,
                                          startangle=45,
                                          explode=explode)

        ax.legend(
            wedges,
            languages,
            title=item_name,
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=24,
            title_fontsize=28
        )

        plt.setp(autotexts, size=18, weight=700)
        ax.set_title(title, fontsize=46)

        plt.show()


def func(pct, allvals):
    absolute = int(pct / 100. * np.sum(allvals))
    return "{:.1f}% ({:d} )".format(pct, absolute)
