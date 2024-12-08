from picture_generator import PictureGenerator


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


def main() -> None:
    repo_list: list[RepoItemInfo] = [
        RepoItemInfo("Python", 150),
        RepoItemInfo("JavaScript", 120),
        RepoItemInfo("Java", 100),
        RepoItemInfo("C++", 80),
        RepoItemInfo("Ruby", 40),
        RepoItemInfo("C#", 90),
        RepoItemInfo("PHP", 60),
        RepoItemInfo("Go", 50),
        RepoItemInfo("Swift", 70),
        RepoItemInfo("Kotlin", 55),
    ]

    PictureGenerator.generate_histogram_picture(
        repo_list, "name", "count", "histogram_picture", "language", "count"
    )
    PictureGenerator.generate_pie_picture(repo_list, "Pie_picture", "language")


if __name__ == "__main__":
    main()
