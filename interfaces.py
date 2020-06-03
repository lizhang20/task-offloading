import abc


class BaseInterfaces(abc.ABC):

    @abc.abstractmethod
    def print_all_interfaces(self):
        raise NotImplementedError("Interfaces must implement a printAllInterfaces method")

    @abc.abstractmethod
    def test_interfaces(self):
        raise NotImplementedError("Interfaces must implement a testInterfaces method")


class BDInterfaces(BaseInterfaces):

    def print_all_interfaces(self):
        pass

    def interfaces1(self):
        pass

    def interfaces2(self):
        pass

    def test_interfaces(self):
        pass
