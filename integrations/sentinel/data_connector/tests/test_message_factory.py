# Copyright (c) 2023 WithSecure. All rights reserved
# Distribured under Apache 2.0 license

import json
import os

import pytest

from app.lib.message_factory import MessageFactory
from app.lib.withsecure_client import SecurityEvent

sut = MessageFactory()


@pytest.mark.parametrize(
    "file, message",
    [
        ("amsi-infection-block.json", 'AMSI detected harmful content in "cscript.exe"'),
        (
            "application-control-error-event.json",
            'Application Control ignored rule "Block malicious '
            'files in Downloads folder"',
        ),
        (
            "application-control-event.json",
            'Application Control blocked application_start of "some product name" based on rule "rule '
            'name"',
        ),
        (
            "application-control-file-access-block-event.json",
            "Application Control blocked "
            "file_access of "
            '"C:\\Users\\gtn-user'
            '\\protected_document.txt" based on '
            'rule "file access test"',
        ),
        (
            "application-control-file-access-report-event.json",
            "Application Control reported "
            "file_access of "
            '"C:\\Users\\gtn-user'
            '\\protected_document.txt" based on '
            'rule "file access test"',
        ),
        (
            "application-control-installation-start-block-event.json",
            "Application Control blocked "
            "installation_start of "
            '"C:\\Windows\\System32'
            '\\msiexec.exe" based on rule '
            '"Default block rule"',
        ),
        (
            "application-control-report-event.json",
            "Application Control reported application_start "
            'of "some product name" based on rule ""',
        ),
        (
            "connection-control-connection-blocked-event.json",
            "Network connection is blocked by "
            "Connection control. Blocked process: "
            '"plink.exe"',
        ),
        (
            "connection-control-page-blocked-event.json",
            "Network connection is blocked by Connection "
            'control. Blocked process: "msedge.exe"',
        ),
        (
            "connection-control-remote-access-blocked-event.json",
            "Network connection is blocked by "
            "Connection control. Blocked "
            'process: "teamviewer.exe"',
        ),
        ("data-guard-event.json", 'DataGuard blocked access to "aUoV1.exe"'),
        ("data-guard-event_ransomware.json", 'DataGuard blocked access to "HELP.doc"'),
        ("data-guard-v2-report-event.json", 'DataGuard reported access to "aUoV1.exe"'),
        ("data-guard-v2-vault.json", 'DataGuard blocked access to "test.txt"'),
        ("deep-guard-event.json", 'Common file "N/A" was blocked'),
        (
            "deep-guard-event-v2.json",
            'The application "N/A" was blocked by the administrator',
        ),
        (
            "deep-guard-event_command_line.json",
            'Rare application was detected in file "N/A" and it ' "was blocked",
        ),
        (
            "device-control-event.json",
            'The device "Intel(R) 82371SB PCI to USB Universal Host '
            'Controller" was blocked based on the following rule: "USB '
            'Mass Storage Devices"',
        ),
        (
            "device-control-execution-event.json",
            "An attempt to execute files on the following "
            'device was blocked: "Intel(R) 82371SB PCI to USB '
            'Universal Host Controller"',
        ),
        (
            "file-scanning-v1-event.json",
            '"ta-Infection:W32/F-Secure_rolajozu.A" was detected on '
            'accessing "[1] f11.exe" and it was disinfected',
        ),
        (
            "file-scanning-v1-no-subscription-event.json",
            '"ta-Infection:W32/F-Secure_rolajozu.A" was '
            'detected on accessing "noh" and it was '
            "disinfected",
        ),
        (
            "file-scanning-v1-sp.evt.fixinf.alert.json",
            '"Riskware:W32/F-Secure_testfile.A" was '
            'detected on accessing "f6[1].exe" and it was'
            " blocked",
        ),
        (
            "file-scanning-v1-sp.evt.fixinf.riskware.alert.json",
            '"Riskware:W32/F-Secure_testfile.A" '
            'was detected on accessing "f6['
            '1].exe" and it was blocked',
        ),
        (
            "file-scanning-v1-sp.evt.oas.alert.json",
            '"Riskware:W32/F-Secure_testfile.A" was detected '
            'on accessing "f6[1].exe" and it was blocked',
        ),
        (
            "file-scanning-v1-sp.evt.oas.alert_with_meta.json",
            '"TR/AD.TestFile.Y" was detected on '
            "accessing "
            '"ad2-test-nv0-mv80-0-with-overlay.exe'
            '" and it was quarantined',
        ),
        (
            "file-scanning-v1-sp.evt.ods.alert.json",
            '"TR/AD.TestFile.Y" was detected on accessing '
            '"ad2-test-nv0-mv80-0-with-overlay.exe" and it '
            "was quarantined",
        ),
        (
            "file-scanning-v2-file-infection-artificial.json",
            '"riskware" was detected on accessing ' '"A" and no action was taken',
        ),
        (
            "file-scanning-v2-file-infection-on-demand-linux.json",
            '"riskware" was detected on ' 'accessing "A" and no action was ' "taken",
        ),
        (
            "file-scanning-v2-spyware-artificial.json",
            '"spyware" was detected on accessing "A" and no action was taken',
        ),
        (
            "file-scanning-v2-system-infection-artificial.json",
            '"EICAR_Test_File" was detected on accessing "eicar.com" and no action was taken',
        ),
        (
            "firewall-fs_rule_triggered-block.json",
            'Connection from "15.170.0.0" was blocked',
        ),
        (
            "integrity-checker-v2-file-modified-action-allow.json",
            "Integrity checker event. Action " "taken: Allow",
        ),
        (
            "integrity-checker-v2-file-modified-action-deny.json",
            "Integrity checker event. Action " "taken: Deny",
        ),
        (
            "integrity-checker-v2-process-modifying-file-alert.json",
            "Integrity checker event. Action " "taken: None",
        ),
        (
            "integrity-checker-v2-process-modifying-file-alert-no-process-path.json",
            "Integrity " "checker event. " "Action taken: " "None",
        ),
        (
            "manual-scanning-v1-event.json",
            '"Spyware:W32/F-Secure_testfile.A" was detected on '
            'accessing "f8.exe" and it was quarantined',
        ),
        (
            "online-safety-category-page-blocked-event.json",
            "Web content control blocked webpage due "
            'to category "social_networking" being '
            "disallowed",
        ),
        (
            "online-safety-category-page-blocked-event_url.json",
            "Web content control blocked webpage "
            'due to category "social_networking"'
            " being disallowed",
        ),
        (
            "online-safety-denied-page-blocked-event.json",
            "Webpage was blocked due to domain name " "being blocked",
        ),
        (
            "online-safety-denied-page-blocked-event_url.json",
            "Webpage was blocked due to domain " "name being blocked",
        ),
        ("online-safety-event.json", 'Action: "Blocked" Subject: "N/A"'),
        ("online-safety-event_url.json", 'Action: "Blocked" Subject: "N/A"'),
        (
            "online-safety-harmful-page-blocked-event.json",
            'Webpage "hxxps://malicious.fstestdomain'
            '.com" was blocked due to reputation '
            "rated harmful",
        ),
        (
            "online-safety-illegal-page-blocked-event.json",
            'Webpage "hxxps://illegal.fstestdomain'
            '.com" was blocked due to reputation '
            "rated prohibited",
        ),
        ("product-setting-changed.json", "Real-time scanning was turned off"),
        (
            "realtime-scanning-v1-event.json",
            '"Testfile:W64/Memtest.A!Mem" was detected on accessing '
            '"" and it was quarantined',
        ),
        (
            "tamper-protection-file-blocked-event.json",
            '"initiator_path" was blocked from deleting ' '"fshoster32.exe"',
        ),
        (
            "tamper-protection-process-blocked-event.json",
            "Tamper protection protected " '"fshoster32.exe" from "initiator_path"',
        ),
        (
            "tamper-protection-registry-blocked-event.json",
            '"initiator_path" was blocked from '
            "deleting a key at "
            '"HKLM\\Software\\F-Secure"',
        ),
        (
            "tamper-protection-service-blocked-event.json",
            'Service "fshoster" was blocked from stop',
        ),
        (
            "tamper-protection-service-blocked-event_with_initiator.json",
            'Service "fshoster" was ' "blocked from stop",
        ),
        (
            "tamper-protection-uninstall-blocked-event.json",
            '"CCleaner64.exe" was blocked from ' "uninstalling the product",
        ),
        (
            "web-traffic-scanning-event.json",
            "The malicious web page "
            '"hxxp://www.gtn/test_samples/ransomware/r3testsample'
            '.exe" accessed by "microsoftedgecp.exe" was blocked',
        ),
        (
            "web-traffic-scanning-event-without-alert-source.json",
            "The malicious web page "
            '"hxxp://www.gtn/test_samples'
            '/ransomware/r3testsample.exe" '
            'accessed by "microsoftedgecp.exe" '
            "was blocked",
        ),
        (
            "web_traffic_scanning_content_type_block.json",
            'The web page "hxxp://unrated.fstestdomain'
            '.com" accessed by "chrome.exe" was '
            "blocked due to content type restrictions",
        ),
        (
            "web_traffic_scanning_url_block.json",
            "The malicious web page "
            '"hxxp://unrated.fstestdomain.com" accessed by '
            '"chrome.exe" was blocked',
        ),
        (
            "xfence-blocked.json",
            "XFENCE blocked write access to "
            '"/Users/test/Desktop/.dat.nosync0b46.NUgzBZ"',
        ),
    ],
)
def test_message_factory(file, message):
    file_directory = os.path.dirname(__file__)
    with open(f"{file_directory}/events/{file}") as event_file:
        event = json.load(event_file)
        result = sut.get_message(SecurityEvent(**event))
        assert result == message
