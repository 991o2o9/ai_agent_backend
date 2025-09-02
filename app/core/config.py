from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    HUGGINGFACE_API_TOKEN: str
    HUGGINGFACE_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"
    
    MAX_TOKENS: int = 512
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9

    SHORT_MEMORY_TTL: int = 3600  # 1 hour
    LONG_MEMORY_LIMIT: int = 100

    MAX_REQUESTS_PER_MINUTE: int = 60
    MAX_REQUESTS_PER_HOUR: int = 1000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance
settings = Settings()
