import os
import logging
import subprocess

from diagnostics import Diagnostics
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class ShutdownServers:

    @staticmethod
    def shutdown_servers(servers: list[str]):
        """
        Главная функция выключения серверов.
        В зависимости от платформы(Windows или Linux) запускает необходимую функцию выключения
        """
        os_name = Diagnostics.get_os()
        if os_name == "Windows":
            for server_ip in servers:
                ShutdownServers.shutdown_servers_by_windows(server_ip)
        elif os_name == "Linux":
            for server_ip in servers:
                ShutdownServers.shutdown_servers_by_linux(server_ip)
        else:
            pass

    @staticmethod
    def shutdown_servers_by_windows(server_ip) -> None:
        """
        Выключает сервера отправкой команды Windows - shutdown.
        Скрипт необходимо запускать с необходимыми привелегиями.
        У сервера должен быть открыт 445 порт.
        """
        try:
            # Пример команды: shutdown /s /m \\10.172.2.70 /t 0
            command = rf'shutdown /s /m \{server_ip} /t 0'
            os.system(command)
            logging.info(f"Команда на отключение отправлена серверу {server_ip}.")
        except Exception as error:
            logging.error(f"Ошибка при отключении сервера {server_ip}: {error}")

    @staticmethod
    def shutdown_servers_by_linux(server_ip) -> None:
        """
        Выключает сервера отправкой команды Linux - net rpc shutdown.
        Работает с доменными логинами и паролями. У учетной записи должны быть права на выключение сервера.
        У сервера должен быть открыт 445 порт. Необходимы пакеты samba samba-common
        Логин и пароль берет из переменных окружения
        """
        username = os.getenv('DOMAIN_USERNAME')
        password = os.getenv('DOMAIN_PASSWORD')

        command = [
            'net', 'rpc', 'shutdown', '-I', server_ip,
            '-U', f'{username}%{password}'
        ]

        try:
            subprocess.run(command, check=True)
            print(f"Команда на выключение сервера {server_ip} успешно отправлена.")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выключении сервера {server_ip}: {e.stderr.strip()}")

