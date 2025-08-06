import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  # Уровень логирования
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/element-bot.log"),  # Логирование в файл
            logging.StreamHandler()  # Логирование в консоль
        ]
    )