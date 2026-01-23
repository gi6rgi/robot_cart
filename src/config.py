from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    image_logs_dir: str
    action_logs_dir: str


class GeminiSettings(BaseSettings):
    api_key: str
    model: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_file=".env")

    gemini: GeminiSettings
    app: AppSettings


settings = Settings()
