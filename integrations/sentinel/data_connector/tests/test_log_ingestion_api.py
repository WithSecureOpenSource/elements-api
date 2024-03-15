# Copyright (c) 2023 WithSecure. All rights reserved
# Distribured under Apache 2.0 license

from unittest.mock import MagicMock

from pytest import raises
from azure.core.exceptions import HttpResponseError

from app.lib.log_ingestion_api import IngestionApiClient

TEST_DCR_STREAM = "Custom-WsSecurityEvents_CL"
TEST_DCR_RULE = "test-dcr-rule"


class MockAzureIngestionClient:
    def __init__(self):
        self.upload = MagicMock()


def test_upload_events():
    azure_mock = MockAzureIngestionClient()
    sut = IngestionApiClient(azure_mock, TEST_DCR_RULE, TEST_DCR_STREAM)

    sut.upload_events([{"PersistenceTimestamp": "2023-01-14"}])

    azure_mock.upload.assert_called_with(
        rule_id=TEST_DCR_RULE,
        stream_name=TEST_DCR_STREAM,
        logs=[{"PersistenceTimestamp": "2023-01-14"}],
    )


def test_upload_events_exception():
    azure_mock = MockAzureIngestionClient()
    azure_mock.upload.side_effect = HttpResponseError()
    sut = IngestionApiClient(azure_mock, TEST_DCR_RULE, TEST_DCR_STREAM)

    with raises(Exception, match="Couldn't send data to Azure"):
        sut.upload_events([{"PersistenceTimestamp": "2023-01-14"}])

        azure_mock.upload.assert_called_with(
            rule_id=TEST_DCR_RULE,
            stream_name=TEST_DCR_STREAM,
            logs=[{"PersistenceTimestamp": "2023-01-14"}],
        )
