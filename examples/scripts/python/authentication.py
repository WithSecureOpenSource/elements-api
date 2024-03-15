# Run client authentication. Add environment variables WS_CLIENT_ID and WS_SECRET with client
# credentials and optionaly WS_API_URL with Elements API url.
#
# Copyright (c) 2023 WithSecure. All rights reserved
# Distribured under Apache 2.0 license

import requests

from json import *
from base64 import b64encode
from os import environ

DEFAULT_URL = "https://api.connect.withsecure.com"
API_URL = environ.get("WS_API_URL", DEFAULT_URL)


# Function that authenticates given client, that is identified by credentials pair
# (client_id, client_secret)
def authenticate(client_id, client_secret):
    auth_header = b64encode(bytes(client_id + ":" + client_secret, "utf-8")).decode(
        "utf-8"
    )
    headers = {
        "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept": "application/json",
        "Authorization": "Basic " + auth_header,
        "User-Agent": "my-script",  # each request must contain User-Agent header
    }
    scopes = ["connect.api.read", "connect.api.write"]  # authenticated client can read
    # and write data

    data = {"grant_type": "client_credentials", "scope": " ".join(scopes)}

    response = requests.post(API_URL + "/as/token.oauth2", data=data, headers=headers)
    if response.ok:
        res_body = response.json()
        return res_body["access_token"]
    else:
        print("Response=" + response.text)
        print("Headers=" + str(response.headers))

        # Each response contains header `X-Transaction`. It can be send to Elements API
        # support team in order to help investigation of possible errors
        print("Transaction-id=" + response.headers.get("X-Transaction"))
        raise Exception("Authentication failed")


if __name__ == "__main__":
    import os
    import sys

    client_id = os.environ.get("WS_CLIENT_ID")
    secret = os.environ.get("WS_SECRET")
    if not client_id or not secret:
        print("WS_CLIENT_ID and WS_SECRET enviornment variables must be defined")
        sys.exit(0)
    token = authenticate(client_id, secret)
    print("Access token:", token)
