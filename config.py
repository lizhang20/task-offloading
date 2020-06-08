class Config:
    server_list = {
        "PC": "127.0.0.1",
        "vagrant-ubuntu": "192.168.56.2",
    }

    decision_algorithm = {
        "default": "select_random_server",
        "minimum_ping_delay": "select_min_ping_server",
    }


class FlaskTestConfig(Config):
    server_list = {
        "PC": "127.0.0.1",
        "vagrant-ubuntu": "192.168.56.2",
    }


class SmartContractConfig(Config):
    # This is a dict containing pairs of <function name: string, offloading or not: bool>
    # Engine will search in this dict to determine whether to offload or not.
    # Example:
    # offloadingFlag = {
    #                   "getRemoteInfo": True,
    #                   "listNodes": False,
    #                   }
    offloadingFlag = dict()

    def __init__(self):
        pass


config = {
    "default": Config,
    "FlaskTestConfig": FlaskTestConfig,
    "SmartContractConfig": SmartContractConfig,
}