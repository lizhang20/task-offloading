import abc

from loguru import logger


class BaseInterfaces(abc.ABC):

    @abc.abstractmethod
    def list_all_interfaces(self):
        raise NotImplementedError("Interfaces must implement a printAllInterfaces method")


class FlaskTestInterfaces(BaseInterfaces):
    default_port: int = 5000

    def list_all_interfaces(self):
        logger.info("Get all interfaces of class: FlaskTestInterfaces")
        method_list = [func for func in dir(FlaskTestInterfaces) if
                       callable(getattr(FlaskTestInterfaces, func)) and not func.startswith("__")]
        for method in method_list:
            print(method)

    @staticmethod
    def hello_world():
        return f"hello"

    @staticmethod
    def get_double(num):
        return f"offloading/{num}"

    @staticmethod
    def get_server():
        return f"getserverlists"


class BDInterfaces(BaseInterfaces):
    default_port: int = 8080
    url_prefix: str = "SCIDE/"

    def list_all_interfaces(self):
        logger.info("Get all interfaces of class: BDInterfaces")
        method_list = [func for func in dir(BDInterfaces) if
                       callable(getattr(BDInterfaces, func)) and not func.startswith("__")]
        for method in method_list:
            print(method)

    @staticmethod
    def ping_pong():
        return BDInterfaces.url_prefix + "SCManager?action=ping"

    @staticmethod
    def list_CProcess():
        return BDInterfaces.url_prefix + "SCManager?action=listContractProcess"

    def interfaces2(self):
        pass
