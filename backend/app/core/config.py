from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Smart Mandi API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://smart_mandi:change_this_local_password@localhost:5433/smart_mandi"
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    supabase_url: str = ""
    admin_user_ids: str = ""
    demo_data_enabled: bool = True
    data_gov_in_api_key: str = ""
    data_gov_in_api_url: str = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    data_gov_in_limit: int = 100

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [x.strip() for x in self.frontend_origins.split(",") if x.strip()]

    @property
    def admin_ids(self) -> set[str]:
        return {x.strip() for x in self.admin_user_ids.split(",") if x.strip()}

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
