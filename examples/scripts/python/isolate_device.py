# Copyright (c) 2024 WithSecure. All rights reserved
# Distribured under Apache 2.0 license

from datetime import datetime, timezone, timedelta
from time import sleep
from os import environ

import requests

from authentication import authenticate

DEFAULT_URL = "https://api.connect.withsecure.com"
API_URL = environ.get("WS_API_URL", DEFAULT_URL)
OPERATIONS_PATH = "/devices/v1/operations"


# Get list of remote operations that were issued for given device
def get_device_operations(auth_token, device_id):
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + auth_token,
        "User-Agent": "my-script",
    }

    params = {"deviceId": device_id}

    response = requests.get(API_URL + OPERATIONS_PATH, params=params, headers=headers)

    if not response.ok:
        print("Error", response.text)
        raise Exception("Request error")

    return response.json()


# Isolate given device from network
def trigger_isolation(auth_token, device_id):
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + auth_token,
        "User-Agent": "my-script",
        "Content-Type": "application/json",
    }

    body = {
        "operation": "isolateFromNetwork",
        "targets": [device_id],
        "parameters": {"message": "Your device is isolated"},
    }

    response = requests.post(API_URL + OPERATIONS_PATH, json=body, headers=headers)

    if response.status_code != 207:
        print("Error", response.text)
        raise Exception("Request error")

    return response.json()


# Triggers remote operation on given device and periodically checks
# status of operation until it is finished
def isolate_and_wait(client_id, client_secret, device_id):
    auth_token = authenticate(client_id, client_secret)

    op = trigger_isolation(auth_token, device_id)
    operation = op["multistatus"][0]
    if operation["status"] == 202:
        op_id = operation["operationId"]
        attempt = 0
        poll_interval = 30
        while attempt < 10:
            sleep(poll_interval)
            device_ops = get_device_operations(auth_token, device_id)
            for it in device_ops["items"]:
                if it["id"] == op_id:
                    op_status = it["status"]
                    if op_status == "finished":
                        # Operation is finished so we can stop top level loop
                        attempt = 10
                    print("Status of operation {} = {}".format(op_id, op_status))
                    break
            attempt += 1
    else:
        print("Unexpected status of execution ", operation["status"])


if __name__ == "__main__":
    import os
    import sys

    client_id = os.environ.get("WS_CLIENT_ID")
    secret = os.environ.get("WS_SECRET")
    if not client_id or not secret:
        print("WS_CLIENT_ID and WS_SECRET enviornment variables must be defined")
        sys.exit(0)
    isolate_and_wait(client_id, secret, sys.argv[1])
