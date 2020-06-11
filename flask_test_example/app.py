from flask import Flask, jsonify
from time import sleep
import random


app = Flask(__name__)


@app.route("/hello")
def hello_world():
    return "world"


@app.route("/offloading/<num>")
def get_double(num):
    sleep(random.randint(0, 10))
    return f"{float(num)**2}"


@app.route("/getserverlists")
def get_server():
    servers = ["127.0.0.1", "192.168.56.2"]
    return jsonify({"data": servers})
