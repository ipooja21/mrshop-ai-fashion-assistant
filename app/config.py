from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    llm_model: str = "gpt-5.6-luna"
    llm_timeout_seconds: float = 10.0
    llm_max_retries: int = 2

    db_path: str = "mrshop.db"
    faiss_index_path: str = "memory.faiss"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()