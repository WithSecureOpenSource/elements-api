# Poll EDR incidents and detections. Add environment variables WS_CLIENT_ID and WS_SECRET
# with client credentials and optionaly WS_API_URL with Elements API url and WS_ORG_ID with
# id of organization that should be queried.
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
INCIDENTS_PATH = "/incidents/v1/incidents"
DETECTIONS_PATH = "/incidents/v1/detections"


def get_updated_incidents(auth_token, min_date, org_id=None, next_page=None):
    headers = {
        "Accept": "application/json",  # always use that header if you expect JSON response
        "Authorization": "Bearer " + auth_token,
        "User-Agent": "my-script",
    }

    params = {
        "limit": 50,
        "updatedTimestampStart": min_date,  # read all incidents updated AFTER `min_date`
        "order": "asc",  # ascending order by `updateTimestampStart`
    }

    # `min_date` represents timestamp of last event in previous page
    # That event should not be included in next respose. When `exclusiveStart=true` is set
    # then `updatedTimestampStart` is used as exclusive start of time range.
    params["exclusiveStart"] = "true"

    if next_page:
        params["anchor"] = next_page

    if org_id:
        params["organizationId"] = org_id

    response = requests.get(API_URL + INCIDENTS_PATH, params=params, headers=headers)

    if not response.ok:
        print("Error", response.text)
        raise Exception("Request error")

    return response.json()


def get_new_detections_page(auth_token, incident_id, min_date, next_page=None):
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + auth_token,
        "User-Agent": "my-script",
    }

    params = {"limit": 100, "incidentId": incident_id}
    if next_page:
        params["anchor"] = next_page

    response = requests.get(API_URL + DETECTIONS_PATH, params=params, headers=headers)

    if not response.ok:
        print("Error", response.text)
        raise Exception("Request error")

    return response.json()


def print_all_detections(auth_token, incident_id, min_date):
    next_page = None
    fetch_page = True
    while fetch_page:
        page = get_new_detections_page(auth_token, incident_id, min_date, next_page)
        next_page = page.get("nextAnchor")
        fetch_page = next_page is not None
        for det in page["items"]:
            print(
                "Detection={}, IncidentId={}".format(
                    det["detectionId"], det["incidentId"]
                )
            )


def get_incidents_updated_after(auth_token, min_dt, org_id):
    # Elements API accepts timestamps in [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339#section-5.6)
    # format: YYYY-MM-DDThh:mm:ss.fff
    last_date = min_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    next_page = None
    fetch_page = True
    print("Reading incidents updated after {}".format(last_date))
    updated_incidents = []
    while fetch_page:
        page = get_updated_incidents(auth_token, last_date, org_id, next_page)
        next_page = page.get("nextAnchor")

        # If `nextAnchor` is present we should fetch next page in next iteration
        fetch_page = next_page is not None
        for incident in page["items"]:
            print(
                "IncidentId={}, Updated Ts={}".format(
                    incident["incidentId"], incident["updatedTimestamp"]
                )
            )
            # updating `last_date` with time when incident was updated
            # when iteration ends, `last_date` will be equal to `updatedTimestamp`
            # of last received incident
            last_date = incident["updatedTimestamp"]
            updated_incidents.append((incident["incidentId"], last_date))

    # Parse timesamp of last received incident after reading all
    # events, that were created after `min_dt`
    return {
        "last_date": datetime.strptime(last_date, "%Y-%m-%dT%H:%M:%S.%fZ"),
        "updated_incidents": updated_incidents,
    }


def poll_edr_detections(client_id, client_secret, poll_interval, org_id=None):
    # initialize start date with current timestamp
    last_date = datetime.now(timezone.utc)

    # start infinite loop
    while True:
        # obtain authentication token
        auth_token = authenticate(client_id, client_secret)

        # read all incdients created after `last_date`. After reading all items
        # that variable is updated with timestamp of last incident. `last_date` will be
        # used in next iteration
        updates = get_incidents_updated_after(auth_token, last_date, org_id)
        last_date = updates["last_date"]
        print("Last date", last_date)
        for incident in updates["updated_incidents"]:
            print_all_detections(auth_token, incident[0], incident[1])
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
    poll_edr_detections(client_id, secret, 60, org_id=org_id)
