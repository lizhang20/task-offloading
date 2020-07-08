import time

from flask import Flask, jsonify, request
from loguru import logger

from engine import DecisionEngine, TaskInfo
from server import ServerList, BDContractServerList
from interfaces import BDInterfaces

app = Flask(__name__)
server_list = BDContractServerList()
# DecisionEngine instance's decision algorithm: minimum_ping_delay
# see more info in config.py
de = DecisionEngine(decision_algorithm="default",
                    server_list=server_list,
                    max_workers=20,
                    consider_throughput=True)


# Error handler with invalid interfaces on this flask server
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error="404 Not Found"), 404


app.register_error_handler(404, resource_not_found)


@app.route("/ping")
def ping_pong():
    logger.info("Client interface ping_pong(route'/ping') has been called")
    st = time.time()
    task = BDInterfaces.ping_pong()
    ret, server = de.submit_task(task=task, port=BDInterfaces.default_port)
    data = ret.result().text
    total_time = time.time() - st
    return jsonify(
        data=data, server=server, status_code=ret.result().status_code, time=total_time,
        throughput=de.cal_throughput(),
    )


@app.route("/listcontractprocess")
def list_contract_process():
    """
    Call this interface for specific server:
        curl http://localhost:port/listcontractprocess?server=[serverIP]
    """
    logger.info(f"Client interface list_contract_process(url: {request.url}) has been called")
    st = time.time()
    # if value is not set, request.args.get() function will return None
    server_ip = request.args.get("server")
    task = BDInterfaces.list_CProcess()
    ret, server = de.submit_task(task, port=BDInterfaces.default_port, ip=server_ip)
    data = ret.result().text
    total_time = time.time() - st
    return jsonify(
        data=data, server=server, status_code=ret.result().status_code, time=total_time,
        throughput=de.cal_throughput(),
    )


@app.route("/execcontract")
def execute_contract():
    """
    Call this interface:
        curl http://localhost:port/execcontract?contractID=[contractID]&operation=[operation] \
        &arg=[arg]&requestID=[requestID]&server=[serverIP]
    An example is :
        curl http://localhost:port/execcontract?contractID=-620602333&operation=main&arg=hhh
    """
    logger.info(f"Client interface execute_contract(url: {request.url}) has been called")
    st = time.time()
    contract_id = request.args.get("contractID")
    operation = request.args.get("operation")
    arg = request.args.get("arg")
    request_id = request.args.get("requestID")
    server_ip = request.args.get("server")
    task = BDInterfaces.execute_contract(contractID=contract_id, operation=operation, arg=arg, request_id=request_id)
    ret, server = de.submit_task(task, port=BDInterfaces.default_port, ip=server_ip)
    data = ret.result().text
    total_time = time.time() - st
    return jsonify(
        data=data, server=server, status_code=ret.result().status_code, time=total_time,
        throughput=de.cal_throughput(),
    )


@app.route("/hello")
def hello_world():
    """
    Construct hello method on smart contract.

    An example is :
        curl http://127.0.0.1:8899/hello?server=[serverIP]
    """
    logger.info(f"Client interface hello(url: {request.url}) has been called")
    st = time.time()
    task = BDInterfaces.execute_contract(
        contractID="Hello",
        operation="hello",
        arg="hhh",
        request_id="123456",
    )
    server_ip = request.args.get("server")
    ret, server = de.submit_task(task, port=BDInterfaces.default_port, ip=server_ip)
    data = ret.result().text
    total_time = time.time() - st
    return jsonify(
        data=data, server=server, status_code=ret.result().status_code, time=total_time,
        throughput=de.cal_throughput(),
    )


@app.route("/listservers")
def list_servers():
    """
    List current servers in current server list.
    :return: example: {
        "data": [
            "127.0.0.1",
            "192.168.56.2"
        ]
    }
    """
    logger.info(f"Client interface list_servers(route'/listservers') has been called")
    return jsonify(data=de.server_list.convert_to_ip_list())
