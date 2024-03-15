# Copyright (c) 2023 WithSecure. All rights reserved
# Distribured under Apache 2.0 license

import json

from app.lib.events_formatter import *
from app.lib.withsecure_client import SecurityEvent


def test_events_formatter():
    sut = Formatter()
    item = {
        "engine": "setting",
        "action": "blocked",
        "persistenceTimestamp": "2023-12-18T11:28:12.594Z",
        "severity": "error",
        "details": {},
        "device": {"winsAddress": "HOST/ta-admin"},
        "organization": {
            "id": "4de503e1-2c58-45c3-89a6-ef3f4a03592b",
            "name": "test company",
        },
    }
    event = SecurityEvent(**item)
    given = sut.format(event)
    expected = {
        "DeviceVendor": "WithSecure",
        "DeviceEventClassID": "setting.blocked",
        "Activity": "Setting event",
        "LogSeverity": 6,
        "DeviceAction": "blocked",
        "SimplifiedDeviceAction": "blocked",
        "PersistenceTimestamp": "2023-12-18T11:28:12.594Z",
        "SourceHostName": "HOST/ta-admin",
        "AdditionalExtensions": "details_accountName=test company",
    }
    assert given.items() >= expected.items()


def test_fileScanning_event():
    sut = Formatter()
    item = {
        "engine": "fileScanning",
        "action": "blocked",
        "persistenceTimestamp": "2023-12-18T11:28:12.594Z",
        "severity": "error",
        "details": {
            "infectionName": "test infection",
            "filePath": "C:/Windows/autoexec.bat",
        },
        "device": {"winsAddress": "HOST/ta-admin"},
        "organization": {
            "id": "4de503e1-2c58-45c3-89a6-ef3f4a03592b",
            "name": "test company",
        },
    }
    event = SecurityEvent(**item)
    given = sut.format(event)
    expected = {
        "DeviceVendor": "WithSecure",
        "DeviceEventClassID": "fileScanning.blocked",
        "Activity": "File Scanning event",
        "DeviceCustomString1": "C:/Windows/autoexec.bat",
        "DeviceCustomString1Label": "Infected object",
        "DeviceCustomString2": "test infection",
        "DeviceCustomString2Label": "Malware",
    }
    assert given.items() >= expected.items()


def test_deepGuard_event_rare_application():
    sut = Formatter()
    item = {
        "engine": "deepGuard",
        "action": "blocked",
        "persistenceTimestamp": "2023-12-18T11:28:12.594Z",
        "severity": "error",
        "details": {
            "name": "DeepGuard blocks a rare application",
            "filePath": "C:/Windows/autoexec.bat",
        },
        "device": {"winsAddress": "HOST/ta-admin"},
        "organization": {
            "id": "4de503e1-2c58-45c3-89a6-ef3f4a03592b",
            "name": "test company",
        },
    }
    event = SecurityEvent(**item)
    given = sut.format(event)
    expected = {
        "DeviceVendor": "WithSecure",
        "DeviceEventClassID": "deepGuard.blocked",
        "Activity": "DeepGuard event",
    }
    not_expected = {
        "DeviceCustomString1",
        "DeviceCustomString1Label",
        "DeviceCustomString2",
        "DeviceCustomString2Label",
    }
    assert given.items() >= expected.items()
    assert not given.keys() >= not_expected


def test_deepGuard_event_regex():
    sut = Formatter()
    item = {
        "engine": "deepGuard",
        "action": "blocked",
        "persistenceTimestamp": "2023-12-18T11:28:12.594Z",
        "severity": "error",
        "details": {
            "name": "Rarity: 1, Reputation: 2",
            "filePath": "C:/Windows/autoexec.bat",
        },
        "device": {"winsAddress": "HOST/ta-admin"},
        "organization": {
            "id": "4de503e1-2c58-45c3-89a6-ef3f4a03592b",
            "name": "test company",
        },
    }
    event = SecurityEvent(**item)
    given = sut.format(event)
    expected = {
        "DeviceVendor": "WithSecure",
        "DeviceEventClassID": "deepGuard.blocked",
        "Activity": "DeepGuard event",
    }
    not_expected = {
        "DeviceCustomString1",
        "DeviceCustomString1Label",
        "DeviceCustomString2",
        "DeviceCustomString2Label",
    }
    assert given.items() >= expected.items()
    assert not given.keys() >= not_expected


def test_deepGuard_event_infection():
    sut = Formatter()
    item = {
        "engine": "deepGuard",
        "action": "blocked",
        "persistenceTimestamp": "2023-12-18T11:28:12.594Z",
        "severity": "error",
        "details": {
            "name": "deepguard infection",
            "filePath": "C:/Windows/autoexec.bat",
        },
        "device": {"winsAddress": "HOST/ta-admin"},
        "organization": {
            "id": "4de503e1-2c58-45c3-89a6-ef3f4a03592b",
            "name": "test company",
        },
    }
    event = SecurityEvent(**item)
    given = sut.format(event)
    expected = {
        "DeviceVendor": "WithSecure",
        "DeviceEventClassID": "deepGuard.blocked",
        "Activity": "DeepGuard event",
        "DeviceCustomString1": "C:/Windows/autoexec.bat",
        "DeviceCustomString1Label": "Infected object",
        "DeviceCustomString2": "deepguard infection",
        "DeviceCustomString2Label": "Malware",
    }
    assert given.items() >= expected.items()


def test_webTrafficScanning_alertType():
    sut = Formatter()
    item = {
        "engine": "webTrafficScanning",
        "action": "blocked",
        "persistenceTimestamp": "2023-12-18T11:28:12.594Z",
        "severity": "error",
        "details": {
            "alertType": "virus",
            "process": "C:\\windows\\explorer.exe",
            "url": "https://example.com",
        },
        "device": {"winsAddress": "HOST/ta-admin"},
        "organization": {
            "id": "4de503e1-2c58-45c3-89a6-ef3f4a03592b",
            "name": "test company",
        },
    }
    event = SecurityEvent(**item)
    given = sut.format(event)
    expected = {
        "DeviceVendor": "WithSecure",
        "DeviceEventClassID": "webTrafficScanning.blocked",
        "Activity": "Web Traffic Scanning event",
        "DeviceCustomString1": "https://example.com",
        "DeviceCustomString1Label": "Infected object",
        "DeviceCustomString2": "explorer.exe",
        "DeviceCustomString2Label": "Malware",
    }
    assert given.items() >= expected.items()


def test_posix_path():
    sut = Formatter()
    item = {
        "engine": "webTrafficScanning",
        "action": "blocked",
        "persistenceTimestamp": "2023-12-18T11:28:12.594Z",
        "severity": "error",
        "details": {
            "alertType": "virus",
            "process": "/home/ta-user/browser.bin",
            "url": "https://example.com",
        },
        "device": {"winsAddress": "HOST/ta-admin"},
        "organization": {
            "id": "4de503e1-2c58-45c3-89a6-ef3f4a03592b",
            "name": "test company",
        },
    }
    event = SecurityEvent(**item)
    given = sut.format(event)
    expected = {
        "DeviceVendor": "WithSecure",
        "DeviceEventClassID": "webTrafficScanning.blocked",
        "Activity": "Web Traffic Scanning event",
        "DeviceCustomString1": "https://example.com",
        "DeviceCustomString1Label": "Infected object",
        "DeviceCustomString2": "browser.bin",
        "DeviceCustomString2Label": "Malware",
    }
    assert given.items() >= expected.items()


def test_webTrafficScanning():
    sut = Formatter()
    item = {
        "engine": "webTrafficScanning",
        "action": "blocked",
        "persistenceTimestamp": "2023-12-18T11:28:12.594Z",
        "severity": "error",
        "details": {
            "filePath": "C:\\windows\\explorer.exe",
            "websiteUrl": "https://example.com",
        },
        "device": {"winsAddress": "HOST/ta-admin"},
        "organization": {
            "id": "4de503e1-2c58-45c3-89a6-ef3f4a03592b",
            "name": "test company",
        },
    }
    event = SecurityEvent(**item)
    given = sut.format(event)
    expected = {
        "DeviceVendor": "WithSecure",
        "DeviceEventClassID": "webTrafficScanning.blocked",
        "Activity": "Web Traffic Scanning event",
        "DeviceCustomString1": "https://example.com",
        "DeviceCustomString1Label": "Infected object",
        "DeviceCustomString2": "explorer.exe",
        "DeviceCustomString2Label": "Malware",
    }
    assert given.items() >= expected.items()


def test_amsi():
    sut = Formatter()
    item = {
        "engine": "amsi",
        "action": "blocked",
        "persistenceTimestamp": "2023-12-18T11:28:12.594Z",
        "severity": "error",
        "details": {
            "path": "C:\\windows\\explorer.exe",
            "infectionName": "AMSI infection",
        },
        "device": {"winsAddress": "HOST/ta-admin"},
        "organization": {
            "id": "4de503e1-2c58-45c3-89a6-ef3f4a03592b",
            "name": "test company",
        },
    }
    event = SecurityEvent(**item)
    given = sut.format(event)
    expected = {
        "DeviceVendor": "WithSecure",
        "DeviceEventClassID": "amsi.blocked",
        "Activity": "Antimalware Scan Interface (AMSI) event",
        "DeviceCustomString1": "C:\\windows\\explorer.exe",
        "DeviceCustomString1Label": "Infected object",
        "DeviceCustomString2": "AMSI infection",
        "DeviceCustomString2Label": "Malware",
    }
    assert given.items() >= expected.items()
