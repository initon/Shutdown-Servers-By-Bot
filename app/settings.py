import json
import sys
import logging

from diagnostics import Diagnostics
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class Settings:
    def __init__(self, path: str):
        config = self.load_config(path)
        try:
            self.MATRIX_URL = config["BOT"]["MATRIX_URL"]
            self.MATRIX_USER = config["BOT"]["MATRIX_USER"]
            self.MATRIX_TOKEN = config["BOT"]["MATRIX_TOKEN"]
            self.ROOM_ID = config["BOT"]["ROOM_ID"]
            self.PERMIT_USERS = config["BOT"]["PERMIT_USERS"]
            self.METHOD_AUTH = config["BOT"]["METHOD_AUTH"]
            self.MATRIX_PASSWORD = config["BOT"]["MATRIX_PASSWORD"]
            self.SERVERS = config["SERVERS"]["IP_ADDRESS_LIST"]
            self.HELP_COMMANDS = config["COMMANDS"]["HELP_COMMANDS"]
            self.TEST_COMMANDS = config["COMMANDS"]["TEST_COMMANDS"]
            self.SHUTDOWN_COMMANDS = config["COMMANDS"]["SHUTDOWN_COMMANDS"]
            self.NETWORK_COMMANDS = config["COMMANDS"]["NETWORK_COMMANDS"]
            self.NETWORK_DEVICES = config["NETWORK_DEVICES"]
            """
            Проверяем наличие переменных окружения, если скрипт запущен в Linux
            """
            if Diagnostics.get_os() == "Linux":
                if not Diagnostics.check_env():
                    logger.error("Не заданы переменные окружения DOMAIN_USERNAME или DOMAIN_PASSWORD")
                    raise SystemExit(1)
        except KeyError as error:
            logger.error(f"Ошибка: отсутствует ключ в конфигурации: {error}")
            raise SystemExit(1)

    @staticmethod
    def load_config(path: str):
        """
        Загружает Json конфигурацию из файла
        """
        try:
            with open(path, encoding='utf-8-sig') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as error:
            logger.error(f"Ошибка загрузки конфигурации: {error}")
            sys.exit(1)
