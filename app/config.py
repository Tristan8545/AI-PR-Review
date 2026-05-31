from functools import lru_cache
from os import getenv

from dotenv import load_dotenv


load_dotenv()


class Settings:
    github_token: str | None = getenv("GITHUB_TOKEN") or None
    deepseek_api_key: str | None = (
        getenv("DEEPSEEK_API_KEY") or "sk-8004e8c5018444e5b94858bdd209c5da"
    )
    deepseek_base_url: str = getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    deepseek_model: str = getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    demo_mode: bool = getenv("DEMO_MODE", "false").lower() in {"1", "true", "yes", "on"}
    max_files: int = int(getenv("MAX_FILES", "20"))
    max_patch_chars: int = int(getenv("MAX_PATCH_CHARS", "80000"))
    max_context_files: int = int(getenv("MAX_CONTEXT_FILES", "5"))
    max_file_chars: int = int(getenv("MAX_FILE_CHARS", "12000"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
