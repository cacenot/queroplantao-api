"""Application configuration using pydantic-settings."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = Field(default="Quero Plantão API", description="Nome da aplicação")
    APP_ENV: Literal["development", "staging", "production"] = Field(
        default="development", description="Ambiente da aplicação"
    )
    DEBUG: bool = Field(default=False, description="Modo debug")
    SECRET_KEY: str = Field(
        default="change-me-in-production", description="Chave secreta da aplicação"
    )
    API_V1_PREFIX: str = Field(default="/api/v1", description="Prefixo da API v1")

    # Server
    HOST: str = Field(default="0.0.0.0", description="Host do servidor")
    PORT: int = Field(default=8000, description="Porta do servidor")
    WORKERS: int = Field(default=1, description="Número de workers")
    RELOAD: bool = Field(
        default=True, description="Reload automático em desenvolvimento"
    )

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost/db",
        description="URL do banco de dados PostgreSQL",
    )

    # Configurações de conexão otimizadas para Neon
    NEON_POOL_SIZE: int = Field(default=5, description="Tamanho do pool de conexões")
    NEON_MAX_OVERFLOW: int = Field(
        default=10, description="Máximo de conexões overflow"
    )
    NEON_POOL_TIMEOUT: int = Field(
        default=30, description="Timeout do pool em segundos"
    )
    NEON_POOL_RECYCLE: int = Field(
        default=3600, description="Reciclar conexões (segundos)"
    )
    NEON_SSL_MODE: str = Field(default="require", description="Modo SSL do Neon")
    NEON_HIBERNATION_TIMEOUT: int = Field(
        default=300, description="Timeout de hibernação"
    )
    NEON_WARM_CONNECTIONS: bool = Field(
        default=True, description="Manter conexões aquecidas"
    )

    # LavinMQ
    LAVINMQ_URL: str = Field(
        default="amqp://guest:guest@localhost:5672/",
        description="URL de conexão do LavinMQ/RabbitMQ",
    )
    LAVINMQ_EXCHANGE: str = Field(
        default="queroplantao", description="Exchange do LavinMQ"
    )
    LAVINMQ_QUEUE_PREFIX: str = Field(default="qp_", description="Prefixo das filas")

    # JWT (Internal - from BFF)
    JWT_SECRET_KEY: str = Field(
        default="change-me-in-production", description="Chave secreta do JWT interno"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256", description="Algoritmo de assinatura JWT"
    )
    JWT_ISSUER: str = Field(default="queroplantao-bff", description="Emissor do JWT")

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Origens permitidas para CORS",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True, description="Permitir credenciais CORS"
    )
    CORS_ALLOW_METHODS: list[str] = Field(
        default=["*"], description="Métodos HTTP permitidos"
    )
    CORS_ALLOW_HEADERS: list[str] = Field(
        default=["*"], description="Headers permitidos"
    )

    # Firebase Authentication
    FIREBASE_PROJECT_ID: str = Field(
        default="",
        description="Firebase Project ID",
    )
    FIREBASE_CREDENTIALS_BASE64: str = Field(
        default="",
        description="Firebase service account credentials JSON encoded in base64",
    )

    # Redis Cache
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="URL de conexão do Redis",
    )
    REDIS_USER_CACHE_TTL: int = Field(
        default=1800,
        description="TTL do cache de usuário em segundos (30 min)",
    )

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Nível de log"
    )
    LOG_FORMAT: Literal["json", "text"] = Field(
        default="json", description="Formato do log"
    )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENV == "production"

    @property
    def database_url_sync(self) -> str:
        """URL síncrona do banco de dados."""
        url = str(self.DATABASE_URL)
        # Remover query params para re-adicionar com os corretos
        base_url = url.split("?")[0]
        return base_url.replace("postgresql://", "postgresql+psycopg://")

    @property
    def database_url_async(self) -> str:
        """URL assíncrona do banco de dados."""
        url = str(self.DATABASE_URL)
        # Remover query params pois asyncpg não aceita sslmode na URL
        # Os parâmetros corretos serão passados em connect_args
        base_url = url.split("?")[0]
        return base_url.replace("postgresql://", "postgresql+asyncpg://")

    @property
    def neon_connection_args_sync(self) -> dict:
        """Argumentos de conexão síncronos otimizados para Neon (psycopg)"""
        return {
            "pool_size": self.NEON_POOL_SIZE,
            "max_overflow": self.NEON_MAX_OVERFLOW,
            "pool_timeout": self.NEON_POOL_TIMEOUT,
            "pool_recycle": self.NEON_POOL_RECYCLE,
            "connect_args": {
                "sslmode": self.NEON_SSL_MODE,
                "connect_timeout": 30,
                "options": "-c default_transaction_isolation=read_committed",
            },
        }

    @property
    def neon_connection_args_async(self) -> dict:
        """Argumentos de conexão assíncronos otimizados para Neon (asyncpg)"""
        return {
            "pool_size": self.NEON_POOL_SIZE,
            "max_overflow": self.NEON_MAX_OVERFLOW,
            "pool_timeout": self.NEON_POOL_TIMEOUT,
            "pool_recycle": self.NEON_POOL_RECYCLE,
            "connect_args": {
                "statement_cache_size": 0,
                "ssl": self.NEON_SSL_MODE == "require",
                "command_timeout": 30,
                "server_settings": {
                    "application_name": "queroplantao_api",
                    "default_transaction_isolation": "read committed",
                },
            },
        }
