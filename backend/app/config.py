"""
app/config.py — Central configuration loaded from environment variables / .env file.

Pydantic-settings reads all values from the environment automatically.
In local dev, python-dotenv loads the .env file before FastAPI starts.
In production (DigitalOcean), set these as environment variables on the droplet.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────
    environment: str = "development"
    log_level: str = "DEBUG"
    cors_origins: str = "http://localhost:5173"  # Comma-separated list

    # ── Database ─────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://miscalibrated:devpassword@localhost:5432/miscalibrated"

    # ── Kafka ─────────────────────────────────────────────────────
    # bootstrap_servers is the entry point for both producers and consumers.
    # In Docker, containers use "kafka:9092"; from the host, use "localhost:29092".
    kafka_bootstrap_servers: str = "localhost:29092"

    # ── Auth0 ─────────────────────────────────────────────────────
    # Auth0 issues JWTs signed with RSA keys. To verify a token, we fetch
    # the public keys from Auth0's JWKS endpoint and check the signature.
    auth0_domain: str = ""
    auth0_audience: str = ""
    auth0_algorithms: list[str] = ["RS256"]

    # ── Kalshi ───────────────────────────────────────────────────
    kalshi_api_key: str = ""
    kalshi_base_url: str = "https://trading-api.kalshi.com/trade-api/v2"

    # ── Polymarket ───────────────────────────────────────────────
    polymarket_clob_url: str = "https://clob.polymarket.com"

    # ── News API ─────────────────────────────────────────────────
    news_api_key: str = ""

    # ── SendGrid ─────────────────────────────────────────────────
    sendgrid_api_key: str = ""
    alert_from_email: str = "alerts@miscalibrated.com"

    # ── LLM ──────────────────────────────────────────────────────
    llm_provider: str = "anthropic"   # "anthropic" or "openai"
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def auth0_jwks_uri(self) -> str:
        """The URL where Auth0 publishes its public signing keys."""
        return f"https://{self.auth0_domain}/.well-known/jwks.json"

    @property
    def auth0_issuer(self) -> str:
        """The expected 'iss' claim in every Auth0 JWT."""
        return f"https://{self.auth0_domain}/"


# Singleton — import this everywhere instead of constructing Settings() each time
settings = Settings()
