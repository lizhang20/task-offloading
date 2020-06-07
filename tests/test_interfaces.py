import unittest

from interfaces import BDInterfaces, FlaskTestInterfaces


class BDinterfacesTestCase(unittest.TestCase):
    def test_bdinterfaces(self):
        bd = BDInterfaces()
        bd.list_all_interfaces()


class FlaskDemoTestCase(unittest.TestCase):
    def test_flask_interfaces(self):
        fsk = FlaskTestInterfaces()
        fsk.list_all_interfaces()


if __name__ == '__main__':
    unittest.main()
