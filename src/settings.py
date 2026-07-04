import os


class Settings:
    """Centralised application configuration loaded from environment variables."""

    def __init__(self) -> None:
        self.SECRET_KEY = "pBP@]BIhwYMGtrVb"
        self.ALGORITHM = "HS256"
        self.TOKEN_EXPIRY_SECONDS = 18000

        # Groq
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        self.GROQ_MODEL_ID = os.getenv("GROQ_MODEL_ID", "groq/llama-3.3-70b-versatile")


settings = Settings()
