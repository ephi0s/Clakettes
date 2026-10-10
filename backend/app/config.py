"""Application configuration via environment variables.

Uses pydantic-settings to load values from a ``.env`` file.
All settings can be overridden via environment variables (prefix optional).

Required for production:
- SECRET_KEY: Must be set to a strong random value
- DATABASE_URL: Must use MariaDB (not SQLite)
- CORS_ORIGINS: Must be explicit domains (not wildcard)
- APP_ENV: Set to "production"
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings for the Clakettes backend.

    Attributes:
        APP_ENV: Runtime environment (development, production, ...).
        DATABASE_URL: SQLAlchemy database connection string.
        SECRET_KEY: Key used for JWT signing.
        ALGORITHM: JWT signing algorithm (default HS256).
        ACCESS_TOKEN_EXPIRE_MINUTES: JWT expiration in minutes.
        CORS_ORIGINS: Optional comma-separated allowed origins.
        PUBLIC_BASE_URL: Public origin of the site, without a trailing slash.
    """

    # Environment: "development", "production", "testing"
    APP_ENV: str = "development"

    # Database: SQLite for dev, MariaDB for prod
    # Examples:
    #   sqlite:///./clakettes.db
    #   mariadb+pymysql://user:pass@host:3306/dbname
    DATABASE_URL: str = "sqlite:///./clakettes.db"

    # JWT secret key - MUST be changed in production!
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # JWT algorithm (HS256 = symmetric, RS256 = asymmetric)
    ALGORITHM: str = "HS256"

    # Access token lifetime in minutes (default 30)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS allowed origins (comma-separated)
    # If None or empty, defaults to ["*"] (allow all)
    # In production, MUST set explicit origins: "https://app.example.com,https://admin.example.com"
    CORS_ORIGINS: str | None = None

    # Public origin clients can reach this deployment on, no trailing slash
    # (e.g. "https://clakettes.com"). Env var: PUBLIC_BASE_URL.
    # Used to emit absolute URLs in generated ICS; RFC 5545 §3.8.4.6 requires
    # URI values to be absolute, so when this is unset the optional URL
    # property is omitted rather than emitted as a relative reference.
    # Defaults to None so a fresh checkout needs no configuration.
    PUBLIC_BASE_URL: str | None = None

    # Pagos online: "mock" por defecto hasta elegir pasarela (stripe/redsys/paypal).
    PAYMENTS_PROVIDER: str = "mock"
    MOCK_PAYMENTS_FORCE_FAIL: bool = False

    # Load from .env file, case-insensitive
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def is_production(self) -> bool:
        """True when running in a production environment (APP_ENV=production)."""
        return self.APP_ENV == "production"

    @property
    def cors_origins_list(self) -> list:
        """Parse ``CORS_ORIGINS`` into a list or return ``["*"]`` (allow all).

        Splits on comma+space for readability in .env files.
        """
        if self.CORS_ORIGINS:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(", ")]
        return ["*"]

    @property
    def cors_allow_credentials(self) -> bool:
        """Allow credentials (cookies/auth) only with explicit origins, never with wildcard.

        Security best practice: wildcard (*) + credentials = vulnerable to CSRF.
        Returns True only when CORS_ORIGINS is explicitly set.
        """
        return bool(self.CORS_ORIGINS and self.CORS_ORIGINS.strip())


# Global settings instance (singleton pattern via module import)
settings = Settings()
