import logging
import os
import platform
import subprocess
from socket import socket, AF_INET, SOCK_STREAM

from netmiko import (
    ConnectHandler
)

from network_manager import NetworkManager
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class Diagnostics:

    @staticmethod
    def get_os() -> str:
        """
        Возвращает название платформы из под которой запущен скрипт
        """
        os_name = platform.system()
        if os_name == "Windows":
            return "Windows"
        elif os_name == "Linux":
            return "Linux"
        else:
            return "Unknown OS"

    @staticmethod
    def check_authentication_devices(devices):
        result = ""
        for device in devices:
            host = device["host"]
            try:
                device_options = NetworkManager.get_device_options(device)
                with ConnectHandler(**device_options) as ssh:
                    ssh.enable()
                    result += f"Аутентификация на сетевом устройстве {host} успешно выполнена. \n"
            except Exception as error:
                result += f"Аутентификация на сетевом устройстве {host} не выполнена. Ошибка: {error} \n"

        return result

    @staticmethod
    def check_servers(servers: list[str]) -> str:
        """
        Проверяет подключение к Windows-серверу и права на выключение.
        """
        message = ""
        for server_ip in servers:
            try:
                check_result_message = ""
                if Diagnostics.get_os() == "Windows":
                    check_result_message = Diagnostics.check_port(server_ip)
                elif Diagnostics.get_os() == "Linux":
                    check_result_message = Diagnostics.check_connection_by_linux(server_ip)
                message += check_result_message + "\n"
            except Exception as error:
                logger.error(f"Ошибка проверки сервера {server_ip}: {error}")
                message += f"Ошибка проверки сервера {server_ip}: {error}\n"
        return message

    @staticmethod
    def check_port(server_ip: str, port: int = 445) -> str:
        """
        Проверяет доступность сервера по 445 порту
        """
        try:
            with socket(AF_INET, SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex((server_ip, port))
        except Exception as error:
            return f"Ошибка при проверке порта {port} на сервере {server_ip}. Ошибка: {error}"

        if result == 0:
            return f"Порт {port} сервера {server_ip} доступен."
        else:
            return f"Порт {port} сервера {server_ip} не доступен. Вероятно, сервер отключен."

    @staticmethod
    def check_env() -> bool:
        """
        Проверяет наличие переменных окружения доменных логина и пароля
        """
        username = os.getenv('DOMAIN_USERNAME')
        password = os.getenv('DOMAIN_PASSWORD')

        if not username or not password:
            return False
        else:
            return True

    @staticmethod
    def get_user_connection() -> str:
        os_platform = Diagnostics.get_os()
        if os_platform == "Linux":
            return os.getenv('DOMAIN_USERNAME')
        elif os_platform == "Windows":
            return os.getlogin()
        else:
            return "Не поддерживаемая платформа."

    @staticmethod
    def check_connection_by_linux(server_ip):
        """
        Проверяет подключение к Windows-серверу и права на выключение.
        """
        username = os.getenv('DOMAIN_USERNAME')
        password = os.getenv('DOMAIN_PASSWORD')

        command = [
            'net', 'rpc', 'info', '-I', server_ip,
            '-U', f'{username}%{password}'
        ]

        try:
            # Выполняем команду и проверяем результат
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = result.stdout

            # Проверяем наличие прав на выключение
            if "Domain Name:" in output:
                return f"Подключение к серверу {server_ip} успешно выполнено."
            else:
                logger.error(f"Неизвестный код ответа от сервера {server_ip}: {output}")
                return f"Неизвестный код ответа от сервера {server_ip}. Проверьте лог."

        except subprocess.CalledProcessError as e:
            output = e.stderr.strip()
            if "NT_STATUS_LOGON_FAILURE" in output:
                return f"Ошибка подключения к {server_ip}. Неправильный логин или пароль!"
            elif "NT_STATUS_HOST_UNREACHABLE" in output:
                return f"Ошибка подключения к {server_ip}. Сервер не доступен."
            elif "Invalid ip address specified" in output:
                return f"Проверьте корректность IP адреса: {server_ip}"
            elif "NT_STATUS_ACCESS_DENIED" in output:
                return f"Ошибка подключения к {server_ip}. Отказано в доступе."
            else:
                logger.error(f"Ошибка подключения к {server_ip}: {output}")
                return f"Ошибка подключения к {server_ip}: {output}"
