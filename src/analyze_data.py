import asyncio
from datetime import datetime

from dateutil.relativedelta import relativedelta
import pandas as pd

from settings import settings
from db import DataBase
from picture_generator import PictureGenerator


async def plot_hist(
    db: DataBase,
    max_date: datetime,
    counts_all: pd.DataFrame,
    counts_last_year: pd.DataFrame,
) -> None:
    counts_all_top_10 = counts_all.nlargest(10, "count")
    counts_all_top_20 = counts_all.nlargest(20, "count")
    PictureGenerator.generate_histogram_picture(
        counts_all_top_10["count"], "Репозитории за 10 лет (10 языков)"
    )
    PictureGenerator.generate_histogram_picture(
        counts_all_top_20["count"], "Репозитории за 10 лет (20 языков)"
    )

    counts_last_year_top_10 = counts_last_year.nlargest(10, "count")
    counts_last_year_top_20 = counts_last_year.nlargest(20, "count")
    PictureGenerator.generate_histogram_picture(
        counts_last_year_top_10["count"],
        "Репозитории за последний год (10 языков)",
    )
    PictureGenerator.generate_histogram_picture(
        counts_last_year_top_20["count"],
        "Репозитории за последний год (20 языков)",
    )


async def plot_pie(
    db: DataBase,
    max_date: datetime,
    counts_all: pd.DataFrame,
    counts_last_year: pd.DataFrame,
) -> None:
    counts_all_top_10 = counts_all.nlargest(10, "count")
    PictureGenerator.generate_pie_picture(
        counts_all_top_10["count"], "Репозитории за 10 лет (10 языков)"
    )
    counts_last_year_top_10 = counts_last_year.nlargest(10, "count")
    PictureGenerator.generate_pie_picture(
        counts_last_year_top_10["count"], "Репозитории за последний год (10 языков)"
    )


async def plot_lines(
    db: DataBase, max_date: datetime, counts_last_year: pd.DataFrame
) -> None:
    top_10_langs = counts_last_year.nlargest(10, "count").index
    top_15_langs = counts_last_year.nlargest(15, "count").index

    counts_by_month_all = await db.get_counts_by_month()
    counts_by_month_all_top_10 = counts_by_month_all.loc[top_10_langs]
    counts_by_month_all_top_20 = counts_by_month_all.loc[top_15_langs]
    PictureGenerator.generate_picture(
        counts_by_month_all_top_10, "Репозитории за 10 лет (10 языков)"
    )
    PictureGenerator.generate_picture(
        counts_by_month_all_top_20, "Репозитории за 10 лет (15 языков)"
    )

    counts_by_month_last_year = await db.get_counts_by_month(
        date_from=max_date - relativedelta(years=1), date_to=max_date
    )
    counts_by_month_last_year_top_10 = counts_by_month_last_year.loc[top_10_langs]
    PictureGenerator.generate_picture(
        counts_by_month_last_year_top_10, "Репозитории за последний год (10 языков)"
    )
    counts_by_month_last_year_top_15 = counts_by_month_last_year.loc[top_15_langs]
    PictureGenerator.generate_picture(
        counts_by_month_last_year_top_15, "Репозитории за последний год (15 языков)"
    )


async def main() -> None:
    db = DataBase(settings.db_url)

    counts_all = await db.get_counts()
    max_date = await db.max_date()
    counts_last_year = await db.get_counts(
        date_from=max_date - relativedelta(years=1), date_to=max_date
    )

    await plot_hist(db, max_date, counts_all, counts_last_year)
    await plot_pie(db, max_date, counts_all, counts_last_year)
    await plot_lines(db, max_date, counts_last_year)


if __name__ == "__main__":
    asyncio.run(main())
