# Poll EPP Security events. Add environment variables WS_CLIENT_ID and WS_SECRET with client
# credentials and optionaly WS_API_URL with Elements API url and WS_ORG_ID with id of
# organization that should be queried.
#
# Copyright (c) 2023 WithSecure. All rights reserved
# Distribured under Apache 2.0 license

from datetime import datetime, timezone
from time import sleep
from os import environ

import requests

from authentication import authenticate

DEFAULT_URL = "https://api.connect.withsecure.com"
API_URL = environ.get("WS_API_URL", DEFAULT_URL)
EVENTS_PATH = "/security-events/v1/security-events"


# Reads single page of events, that were created after given
# timestamp.
def get_events_page(auth_token, min_date, org_id=None, next_page=None):
    headers = {
        "Accept": "application/json",  # always use that header if you expect JSON response
        "Authorization": "Bearer " + auth_token,
        "User-Agent": "my-script",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    params = {
        "limit": 200,
        "engineGroup": ["epp", "edr"],
        "persistenceTimestampStart": min_date,  # read all events created AFTER `min_date`
        "order": "asc",  # ascending order
    }

    # `min_date` represents timestamp of last event in previous page
    # That event should not be included in next respose. When `exclusiveStart=true` is set
    # then `persistenceTimestampStart` is used as exclusive start of time range.
    params["exclusiveStart"] = "true"

    if next_page:
        params["anchor"] = next_page

    if org_id:
        params["organizationId"] = org_id

    response = requests.post(API_URL + EVENTS_PATH, data=params, headers=headers)

    if not response.ok:
        print("Error", response.text)
        raise Exception("Request error")

    return response.json()


# Get all events persisted after `min_dt`. Function reads all pages
# that are produced by request.
def get_events_after(auth_token, min_dt, org_id):
    # Elements API accepts timestamps in [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339#section-5.6)
    # format: YYYY-MM-DDThh:mm:ss.fff
    last_date = min_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    next_page = None
    fetch_page = True
    print("Reading events created after {}".format(last_date))
    while fetch_page:
        page = get_events_page(auth_token, last_date, org_id, next_page)
        next_page = page.get("nextAnchor")

        # If `nextAnchor` is present we should fetch next page in next iteration
        fetch_page = next_page is not None
        for event in page["items"]:
            print(
                "EventId={}, EventTs={}".format(
                    event["id"], event["persistenceTimestamp"]
                )
            )
            # updating `last_date` with time when event was persisted
            # when iteration ends, `last_date` will be equal to `persistenceTimestamp`
            # of last received event
            last_date = event["persistenceTimestamp"]

    # Parse timesamp of last received event after reading all
    # events, that were created after `min_dt`
    return datetime.strptime(last_date, "%Y-%m-%dT%H:%M:%S.%fZ")


def poll_security_events(client_id, client_secret, poll_interval, org_id=None):
    # initialize start date with current timestamp
    last_date = datetime.now(timezone.utc)

    # start infinite loop
    while True:
        # obtain authentication token
        auth_token = authenticate(client_id, client_secret)

        # read all events created after `last_date`. After reading all events
        # that variable is updated with timestamp of last events. `last_date` will be
        # used in next iteration
        last_date = get_events_after(auth_token, last_date, org_id)
        print("Last date", last_date)

        # execute next iteration every `poll_interval`
        sleep(poll_interval)


if __name__ == "__main__":
    import os
    import sys

    client_id = os.environ.get("WS_CLIENT_ID")
    secret = os.environ.get("WS_SECRET")
    if not client_id or not secret:
        print("WS_CLIENT_ID and WS_SECRET enviornment variables must be defined")
        sys.exit(0)
    org_id = os.environ.get("WS_ORG_ID", None)
    poll_security_events(client_id, secret, 60, org_id=org_id)
