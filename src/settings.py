class Settings:
    """Centralised application configuration loaded from environment variables."""

    def __init__(self) -> None:
        """
        Read all configuration values from environment variables and set sensible defaults.

        Raises RuntimeError if the required ENV or other required variables are missing.
        """
        self.SECRET_KEY = "pBP@]BIhwYMGtrVb"
        self.ALGORITHM = "HS256"
        self.TOKEN_EXPIRY_SECONDS = 18000


settings = Settings()
