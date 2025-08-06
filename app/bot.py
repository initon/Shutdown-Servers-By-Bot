import time
import logging
import simplematrixbotlib as botlib

from network_manager import NetworkManager
from diagnostics import Diagnostics
from shutdown_servers import ShutdownServers
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
logging.getLogger('nio').setLevel(logging.CRITICAL)  # Отключаем логгирование nio библиотеки


class MatrixBot:

    def __init__(self, _settings):
        self.settings = _settings
        # Проверяем метод аутентификации
        auth_params = {
            "homeserver": self.settings.MATRIX_URL,
            "username": self.settings.MATRIX_USER,
            "session_stored_file": f"configs/session.txt"
        }

        # Проверяем метод аутентификации и добавляем соответствующий параметр
        if self.settings.METHOD_AUTH == "token":
            auth_params["access_token"] = self.settings.MATRIX_TOKEN
        elif self.settings.METHOD_AUTH == "password":
            auth_params["password"] = self.settings.MATRIX_PASSWORD
        else:
            logging.error(f"Неподдерживаемый метод аутентификации: {self.settings.METHOD_AUTH}")
            raise SystemExit(1)

        # Создаем креды и бота
        self.creds = botlib.Creds(**auth_params)
        self.botMatrix = botlib.Bot(creds=self.creds)

        self.botMatrix.listener.on_message_event(self.main_listener)

    async def main_listener(self, room, message):
        """
        Главная функция обработчика сообщений
        """
        if room.room_id == self.settings.ROOM_ID and message.sender != self.settings.MATRIX_USER:
            if message.sender in self.settings.PERMIT_USERS:
                command_text = str(message.body).lower().strip()
                if command_text in self.settings.HELP_COMMANDS:
                    logger.info(f"Пользователь: {message.sender} запросил справку.")
                    await self.help(room)
                elif command_text in self.settings.TEST_COMMANDS:
                    logger.info(f"Пользователь: {message.sender} запросил статус бота.")
                    await self.test_bot(room)
                elif command_text in self.settings.SHUTDOWN_COMMANDS:
                    logger.info(f"Пользователь: {message.sender} отправил запрос на отключение серверов.")
                    await self.shutdown(room)
                elif command_text in self.settings.NETWORK_COMMANDS:
                    logger.info(f"Пользователь: {message.sender} отправил запрос на отключение сети.")
                    await self.disable_network(room)
                else:
                    logger.info(f"Пользователь отправил неизвестную команду - {message}")
                    await self.botMatrix.api.send_text_message(room.room_id,
                                                               "Неизвестная команда. Для вывода справки введите: "
                                                               "справка")
            else:
                logger.info(f"Пользователь: {message.sender} не опознан.")
                await self.botMatrix.api.send_text_message(room.room_id,
                                                           "У вас нет доступа к командам этого бота! Обратитесь к "
                                                           "администратору бота!")

    async def help(self, room):
        """
        Функция вывода справки в комнату
        """
        help_message = f"""Краткое руководство по использованию бота
Общие правила:

Команды можно вводить в любом регистре: "Тест", "ТеСт", "тест" — все варианты равнозначны.
Допускается наличие пробелов как перед, так и после команды: "Тест ", " Тест ", " Тест".
Команды вводятся без кавычек.

Режимы работы:
1) Отключение серверов.
2) Отключение сети до серверов (не отключает сами серверы). Внимание! Этот режим является резервным 
и используется, если какой-либо из серверов не отключается, или как дополнительная мера.

Доступные команды:

Вывести справку:
- {self.settings.HELP_COMMANDS}
Проверить работу бота и проверить доступность серверов:
- {self.settings.TEST_COMMANDS}
Выключить сервера можно с помощью следующих команд:
- {self.settings.SHUTDOWN_COMMANDS}
Отключить сеть(вспомогательная команда, в случае, если сервера по
какой то причине не отключаются:
- {self.settings.NETWORK_COMMANDS}
По дополнительным вопросам просьба обращаться к администратору бота.
"""
        await self.botMatrix.api.send_text_message(room.room_id, help_message)

    async def test_bot(self, room):
        """
        Функция запуска проверки доступности серверов
        """
        message_check_servers = Diagnostics.check_servers(self.settings.SERVERS)
        result_auth_devices = Diagnostics.check_authentication_devices(self.settings.NETWORK_DEVICES)
        await self.botMatrix.api.send_text_message(room.room_id,
                                                   f"Бот запущен! \nИнформация о системе: {Diagnostics.get_os()}\n"
                                                   f"Имя пользователя: {Diagnostics.get_user_connection()}\n\n"
                                                   f"{message_check_servers}\n{result_auth_devices}")

    async def shutdown(self, room):
        """
        Функция выключения серверов.
        После отправки команды на отключение серверов ждем TIMEOUT_CHECK для проверки
        доступности серверов.
        """
        try:
            await self.botMatrix.api.send_text_message(room.room_id, "Команда на выключение серверов отправлена!")
            # Отправляем команду на выключение серверов
            ShutdownServers.shutdown_servers(self.settings.SERVERS)
        except Exception as error:
            logger.info(f"Произошла ошибка при выключении серверов: {error}")
            await self.botMatrix.api.send_text_message(room.room_id,
                                                       f"Произошла ошибка при выключении серверов: {error}")

    async def disable_network(self, room):
        """
        Функция блокировки доступности серверов с помощью сетевого оборудования.
        """
        message = "Команда на отключение сети отправлена!"
        devices = self.settings.NETWORK_DEVICES
        netManager = NetworkManager(devices)
        netManager.send_commands()
        await self.botMatrix.api.send_text_message(room.room_id, message)

    def run(self):
        """
        Функция запуска бота и подключения к серверу MATRIX
        """
        while True:
            try:
                logger.info(f"Запуск бота...")
                self.botMatrix.run()
            except Exception as error:
                logger.error(f"Ошибка при работе бота: {error}")
                time.sleep(15)
