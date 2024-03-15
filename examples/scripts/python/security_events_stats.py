# Copyright (c) 2024 WithSecure. All rights reserved
# Distribured under Apache 2.0 license

from datetime import datetime, timezone, timedelta

import requests

from authentication import authenticate

DEFAULT_URL = "https://api.connect.withsecure.com"
API_URL = environ.get("WS_API_URL", DEFAULT_URL)
PATH = "/security-events/v1/security-events"
RESPONSE_FORMAT = "application/vnd.withsecure.aggr+json"


def count_by_engine(client_id, client_secret, start_dt, end_dt, org_id=None):
    auth_token = authenticate(client_id, client_secret)

    headers = {
        "Accept": RESPONSE_FORMAT,
        # when `Accept` header has value `application/vnd.withsecure.aggr+json`
        # then API caluclates statistics for events matching query parameters
        "Authorization": "Bearer " + auth_token,
        "User-Agent": "my-script",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    param_start_dt = start_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    param_end_dt = end_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # API selects all security events from `epp` engine group that were persisted
    # between `start_dt` and `end_dt`, group items by value of `engine` property
    # and return number of items in each group
    params = {
        "engineGroup": ["epp"],
        "persistenceTimestampStart": param_start_dt,
        "persistenceTimestampEnd": param_end_dt,
        "count": "engine",  # property `engine` is used to group
    }

    if org_id:
        params["organizationId"] = org_id

    response = requests.post(API_URL + PATH, data=params, headers=headers)

    if not response.ok:
        print("Error", response.text)
        raise Exception("Request error")

    return response.json()


def count_by_engine_last_week(client_id, client_secret, org_id):
    end = datetime.now(tz=timezone.utc)
    start = end - timedelta(days=7)

    stats = count_by_engine(client_id, secret, start, end, org_id)
    fmt = "|{:<30}|{:<15}|"
    print(fmt.format("Engine", "Events count"))
    print("-----------------------------------------------")
    for row in stats["items"]:
        # Every item represent number of Security Events having common value
        # of property `engine`
        print(fmt.format(row["engine"], row["count"]))


if __name__ == "__main__":
    import os
    import sys

    client_id = os.environ.get("WS_CLIENT_ID")
    secret = os.environ.get("WS_SECRET")
    if not client_id or not secret:
        print("WS_CLIENT_ID and WS_SECRET enviornment variables must be defined")
        sys.exit(0)
    org_id = os.environ.get("WS_ORG_ID", None)
    count_by_engine_last_week(client_id, secret, org_id)
