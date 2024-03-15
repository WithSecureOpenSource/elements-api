# Get all EPP devices with critical protection status. Add environment variables WS_CLIENT_ID
# and WS_SECRET with client credentials and optionaly WS_API_URL with Elements API url and
# WS_ORG_ID with id of organization that should be queried.
#
# Copyright (c) 2023 WithSecure. All rights reserved
# Distribured under Apache 2.0 license

import requests

from authentication import authenticate

API_URL = "https://api.connect.withsecure.com"
DEVICES_PATH = "/devices/v1/devices"


# Function read all devices for given Organization, that have status
# `warning` or `critical`. If organization is undefined function selects
# devices under organization of authenticated client
def get_devices(client_id, client_secret, organization_id=None, next_page=None):
    auth_token = authenticate(client_id, client_secret)
    headers = {
        "Accept": "application/json",  # always use that header if you expect JSON response
        "Authorization": "Bearer " + auth_token,
        "User-Agent": "my-script",
    }

    params = {"limit": 10}  # use `limit` to define size of single page

    params["protectionStatusOverview"] = ["critical"]
    # with parameter `protectionStatusOverview` we can read select devices with given
    # protection status.

    if organization_id:
        # `organization_id` parameter is optional. If authenticated client belongs to
        # partner organization, it can use `organization_id` to select devices that
        # belong to given organization
        params["organizationId"] = organization_id

    if next_page:
        params[
            "anchor"
        ] = next_page  # add `anchor` to query parameters to read next page
        # as value use property `nextAnchor` from last response
        # if `nextAnchor` is not present in response it means
        # that query returned last page

    response = requests.get(API_URL + DEVICES_PATH, params=params, headers=headers)

    if not response.ok:
        print("Error", response.text)
        sys.exit(0)

    body = response.json()
    items = body["items"]  # if any device matching query is found then `items`
    # list is empty

    for d in items:
        print(
            "Device name={}, status={}, company={}".format(
                d["name"], d["protectionStatusOverview"], d["company"]["name"]
            )
        )
    if "nextAnchor" in body:
        # if `nextAnchor` is present in response, client can use it to read next page
        # of query result. For example by calling function
        # get_devices_with_status(client_id, client_secret, next_page=response["nextAnchor"])
        print("Link to next page=", body["nextAnchor"])
    else:
        # if `nextAnchor` is missing in response it means, that client received last page
        # of query results
        print("Last page")


if __name__ == "__main__":
    import os
    import sys

    client_id = os.environ.get("WS_CLIENT_ID")
    secret = os.environ.get("WS_SECRET")
    if not client_id or not secret:
        print("WS_CLIENT_ID and WS_SECRET enviornment variables must be defined")
        sys.exit(0)
    org_id = os.environ.get("WS_ORG_ID", None)
    get_devices(client_id, secret, organization_id=org_id)
