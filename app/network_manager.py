import logging
from logging_config import setup_logging

from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException
)

setup_logging()
logger = logging.getLogger(__name__)


class NetworkManager:

    def __init__(self, devices):
        self.devices = devices

    @staticmethod
    def get_device_options(device):
        """
        Функция получает словарь с параметрами для аутентификации на сетевом оборудовании.
        """
        return {
            "device_type": device["device_type"],
            "host": device["host"],
            "username": device["username"],
            "password": device["password"],
            "secret": device["secret"],
            "port": device["port"]
        }

    def send_commands(self):
        """
        Функция отправки команд на сетевое оборудование.
        """
        for device in self.devices:
            try:
                device_options = NetworkManager.get_device_options(device)
                with ConnectHandler(**device_options) as ssh:
                    ssh.enable()
                    host = device["host"]
                    for command in device["commands"]:
                        try:
                            ssh.send_command(command)
                        except Exception as cmd_error:
                            logging.error(f"Ошибка при выполнении команды '{command}' на {host}: {cmd_error}")
            except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
                logging.error(f"Ошибка при отправке команд на устройство {device['host']}: {error}")
            except Exception as e:
                logging.error(f"Необработанное исключение для устройства {device['host']}: {e}")
