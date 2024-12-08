from picture_generator import PictureGenerator
from db import DataBase
import asyncio

# Хранилище
DB_NAME = "data.db"
DB_URL = f"sqlite+aiosqlite:///./{DB_NAME}"


class RepoItemInfo:
    def __init__(self, name: str, count: int):
        self.name = name
        self.count = count

    def __getitem__(self, key):
        if key == "name":
            return self.name
        elif key == "count":
            return self.count
        else:
            raise KeyError(f"Invalid key: {key}")


async def main() -> None:
    db = DataBase(DB_URL)

    counts = await db.get_counts()
    counts = counts.nlargest(20, "count")

    PictureGenerator.generate_histogram_picture(
        counts["count"], "histogram_picture", "language", "count"
    )
    # PictureGenerator.generate_pie_picture(repo_list, "Pie_picture", "language")

    print(await db.min_date())
    print(await db.max_date())
    print(counts["count"])


if __name__ == "__main__":
    asyncio.run(main())
