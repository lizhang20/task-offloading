class Config:
    server_list = {
        "LocalDevice": "127.0.0.1",
        "vagrant-ubuntu": "192.168.56.2",
    }

    decision_algorithm = {
        "default": "select_random_server",
        "minimum_ping_delay": "select_min_ping_server",
    }

    # default_throughput_period is 3 seconds
    DEFAULT_THROUGHPUT_PERIOD = 1

    # User expected throughput in local device, which means that
    # this is max number of requests per second processed on local device,
    # if more than this, offload requests to remote servers.
    EXPECTED_THROUGHPUT = 10


class FlaskTestConfig(Config):
    server_list = {
        "LocalDevice": "127.0.0.1",
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

    server_list = {
        "vagrant-ubuntu": "192.168.56.2",
    }


config = {
    "default": Config,
    "FlaskTestConfig": FlaskTestConfig,
    "SmartContractConfig": SmartContractConfig,
}
