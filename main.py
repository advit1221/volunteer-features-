from bot.core.bot import MaximallyBot
from config import Config


def main() -> None:
    bot = MaximallyBot()
    bot.run(Config.DISCORD_TOKEN)


if __name__ == "__main__":
    main()

