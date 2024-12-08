from picture_generator import PictureGenerator
from db import DataBase
import asyncio

# Хранилище
DB_NAME = "data.db"
DB_URL = f"sqlite+aiosqlite:///./{DB_NAME}"


async def main() -> None:
    db = DataBase(DB_URL)

    counts = await db.get_counts()
    counts = counts.nlargest(20, "count")

    PictureGenerator.generate_histogram_picture(
        counts["count"], "histogram_picture", "language", "count"
    )
    PictureGenerator.generate_pie_picture(counts["count"], "Pie_picture", "language")

    print(await db.min_date())
    print(await db.max_date())
    print(counts["count"])


if __name__ == "__main__":
    asyncio.run(main())
