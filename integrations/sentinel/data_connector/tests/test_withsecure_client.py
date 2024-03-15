# Copyright (c) 2023 WithSecure. All rights reserved
# Distribured under Apache 2.0 license

from app.lib.withsecure_client import *

import json
import os.path

import pytest


class JsonResponse:
    def __init__(self, body, headers={}):
        self.text = json.dumps(body)
        self.body = body
        self.headers = headers
        self.ok = True
        self.headers["X-Transaction"] = headers.get("X-Transaction", "test-tx")

    def json(self):
        return self.body


class RestClient:
    def __init__(self, events=[]):
        self.events = events

    def post(self, url, *args, **kwargs):
        if url.endswith("oauth2"):
            return JsonResponse({"access_token": "test_token"})
        elif url.endswith("security-events"):
            return JsonResponse({"items": self.events})


@pytest.mark.parametrize(
    "file_name",
    [
        ("amsi-infection-block.json"),
        ("web_traffic_scanning_content_type_block.json"),
        ("web_traffic_scanning_url_block.json"),
        ("xfence-blocked.json"),
        ("application-control-error-event.json"),
        ("application-control-event.json"),
        ("application-control-file-access-block-event.json"),
        ("application-control-file-access-report-event.json"),
        ("application-control-installation-start-block-event.json"),
        ("application-control-report-event.json"),
        ("connection-control-connection-blocked-event.json"),
        ("connection-control-page-blocked-event.json"),
        ("connection-control-remote-access-blocked-event.json"),
        ("data-guard-event.json"),
        ("data-guard-event_ransomware.json"),
        ("data-guard-v2-report-event.json"),
        ("data-guard-v2-vault.json"),
        ("deep-guard-event.json"),
        ("deep-guard-event-v2.json"),
        ("deep-guard-event_command_line.json"),
        ("device-control-event.json"),
        ("device-control-execution-event.json"),
        ("file-scanning-v1-event.json"),
        ("file-scanning-v1-no-subscription-event.json"),
        ("file-scanning-v1-sp.evt.fixinf.alert.json"),
        ("file-scanning-v1-sp.evt.fixinf.riskware.alert.json"),
        ("file-scanning-v1-sp.evt.oas.alert.json"),
        ("file-scanning-v1-sp.evt.oas.alert_with_meta.json"),
        ("file-scanning-v1-sp.evt.ods.alert.json"),
        ("file-scanning-v2-file-infection-artificial.json"),
        ("file-scanning-v2-file-infection-on-demand-linux.json"),
        ("file-scanning-v2-spyware-artificial.json"),
        ("file-scanning-v2-system-infection-artificial.json"),
        ("firewall-fs_rule_triggered-block.json"),
        ("integrity-checker-v2-file-modified-action-allow.json"),
        ("integrity-checker-v2-file-modified-action-deny.json"),
        ("integrity-checker-v2-process-modifying-file-alert.json"),
        ("integrity-checker-v2-process-modifying-file-alert-no-process-path.json"),
        ("manual-scanning-v1-event.json"),
        ("online-safety-category-page-blocked-event.json"),
        ("online-safety-category-page-blocked-event_url.json"),
        ("online-safety-denied-page-blocked-event.json"),
        ("online-safety-denied-page-blocked-event_url.json"),
        ("online-safety-event.json"),
        ("online-safety-event_url.json"),
        ("online-safety-harmful-page-blocked-event.json"),
        ("online-safety-illegal-page-blocked-event.json"),
        ("product-setting-changed.json"),
        ("realtime-scanning-v1-event.json"),
        ("tamper-protection-file-blocked-event.json"),
        ("tamper-protection-process-blocked-event.json"),
        ("tamper-protection-registry-blocked-event.json"),
        ("tamper-protection-service-blocked-event.json"),
        ("tamper-protection-service-blocked-event_with_initiator.json"),
        ("tamper-protection-uninstall-blocked-event.json"),
        ("web-traffic-scanning-event.json"),
        ("web-traffic-scanning-event-without-alert-source.json"),
    ],
)
def test_return_security_event(file_name):
    file_directory = os.path.dirname(__file__)
    with open(f"{file_directory}/events/{file_name}") as event_file:
        item = json.load(event_file)
        rc = RestClient([item])
        wc = WithSecureClient(
            "http://api.connect-ci.fsapi.com", "", "", "default", "default", rc
        )
        v = wc.get_events_after("2024-01-01")
        assert v[0].engine == item.get("engine")
