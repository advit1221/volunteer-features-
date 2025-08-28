import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Config:
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    GUILD_ID: str | None = os.getenv("GUILD_ID")
    MAXIMALLY_LOGO_URL: str = os.getenv("MAXIMALLY_LOGO_URL", "")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/profiles.db")


__all__ = ["Config"]

