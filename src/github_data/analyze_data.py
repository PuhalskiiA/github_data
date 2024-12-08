import asyncio

from dateutil.relativedelta import relativedelta

from settings import settings
from db import DataBase
from picture_generator import PictureGenerator


async def main() -> None:
    db = DataBase(settings.db_url)

    counts_all = await db.get_counts()
    counts_all_top_10 = counts_all.nlargest(10, "count")

    PictureGenerator.generate_histogram_picture(
        counts_all_top_10["count"], "histogram_picture_10_years", "language", "count"
    )
    PictureGenerator.generate_pie_picture(
        counts_all_top_10["count"], "pie_picture_10_years", "language"
    )

    max_date = await db.max_date()
    counts_last_year = await db.get_counts(
        date_from=max_date - relativedelta(years=1), date_to=max_date
    )
    counts_last_year_top_10 = counts_last_year.nlargest(10, "count")
    PictureGenerator.generate_histogram_picture(
        counts_last_year_top_10["count"],
        "histogram_picture_last_year",
        "language",
        "count",
    )
    langs = counts_last_year_top_10.index
    print(langs)

    counts_by_month_all = await db.get_counts_by_month()
    counts_by_month_all_top_10 = counts_by_month_all.loc[langs]

    PictureGenerator.generate_picture(
        counts_by_month_all_top_10, "dots", "year", "count"
    )


if __name__ == "__main__":
    asyncio.run(main())
