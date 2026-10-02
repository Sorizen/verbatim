from pathlib import Path

from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import OPENROUTER_BASE_URL
from app.enums import VideoResolution

REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPO_ROOT / '.env'
SQLALCHEMY_SCHEME = 'postgresql+psycopg'
LIBPQ_SCHEME = 'postgresql'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra='ignore')

    OPENROUTER_API_KEY: SecretStr = SecretStr('')
    OPENROUTER_BASE_URL: str = OPENROUTER_BASE_URL
    VIDEO_RESOLUTION: VideoResolution = VideoResolution.P480
    MAX_USD_PER_RUN: float = 8.0

    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5434
    POSTGRES_USER: str = 'holywater'
    POSTGRES_PASSWORD: str = 'holywater'
    POSTGRES_DB: str = 'holywater'

    REDIS_URL: str = 'redis://localhost:6380/0'

    RUNS_DIR: Path = REPO_ROOT / 'runs'
    EXAMPLES_DIR: Path = REPO_ROOT / 'examples'
    CORS_ORIGINS: list[str] = ['http://localhost:5173']

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self._build_dsn(SQLALCHEMY_SCHEME)

    @property
    def CHECKPOINTER_CONNINFO(self) -> str:
        return self._build_dsn(LIBPQ_SCHEME)

    def _build_dsn(self, scheme: str) -> str:
        return str(
            PostgresDsn.build(
                scheme=scheme,
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )


settings = Settings()
