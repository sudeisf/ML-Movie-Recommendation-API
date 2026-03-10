import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    base_dir: Path
    data_dir: Path
    tmdb_api_key: str
    allowed_origins: list[str]
    sample_size: int
    max_recommendations: int


def _parse_allowed_origins(raw_origins: str) -> list[str]:
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["http://localhost:5173"]


def get_settings() -> Settings:
    base_dir = Path(__file__).resolve().parents[2]
    data_dir = Path(os.getenv("DATA_DIR", str(base_dir)))
    tmdb_api_key = os.getenv("TMDB_API_KEY", "").strip()
    allowed_origins = _parse_allowed_origins(os.getenv("ALLOWED_ORIGINS", "http://localhost:5173"))

    sample_size = int(os.getenv("SAMPLE_SIZE", "1000"))
    max_recommendations = int(os.getenv("MAX_RECOMMENDATIONS", "20"))

    return Settings(
        base_dir=base_dir,
        data_dir=data_dir,
        tmdb_api_key=tmdb_api_key,
        allowed_origins=allowed_origins,
        sample_size=sample_size,
        max_recommendations=max_recommendations,
    )


settings = get_settings()
