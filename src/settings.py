from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: str
    debug: bool = True
    path_to_tokens: str
    max_repos: int = 1000
    fetch_years: int = 10

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
