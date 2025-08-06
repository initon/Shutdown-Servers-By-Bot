from bot import MatrixBot
from settings import Settings


def main():
    config_path = 'configs/config.json'
    settings = Settings(config_path)
    bot = MatrixBot(settings)
    bot.run()


if __name__ == '__main__':
    main()
