## A task offloading example serverside code

This is a serverside code for outer `app.py` offloading client.

A `FlaskTestServerList` instance can request `/getserverlists` to initialize its serverList.

### How to run?

1. Install requirements

```
pip install flask
```

2. Use gunicorn or `flask run` command (not recommand) to run this server

```
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```
