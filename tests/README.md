# How to run unittest

Run all unittest on root folder. For some test files, use `sudo` cause of this project use ping command based on ICMP, need `sudo` to send ICMP packages.

## Run specific files

```
python3 -m unittet tests/test_base_server.py
```

## Run specific function or class

Should have `tests/__init__.py`

```
python3 -m unittest tests.test_base_server.ServerListTestCases.test_select_min_ping_server
```

## Run all tests

```
python3 -m unittest
```
