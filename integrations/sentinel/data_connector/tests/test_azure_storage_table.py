# Copyright (c) 2023 WithSecure. All rights reserved
# Distribured under Apache 2.0 license

from unittest.mock import MagicMock

from azure.data.tables import UpdateMode

from app.lib.azure_storage_table import StorageTableClient

PARTITION_KEY = "WithSecureConnectorViaAPI"
ROW_KEY = "LastSuccessfulRead"


class MockAzureTableClient:
    def __init__(self):
        self.create_entity = MagicMock()
        self.update_entity = MagicMock()


def test_save_start_timestamp():
    mock_azure_client = MockAzureTableClient()
    sut = StorageTableClient(mock_azure_client)
    test_ts = "2023-12-11T10:12:55Z"
    sut.save_start_timestamp(test_ts)

    mock_azure_client.update_entity.assert_called_with(
        {"PartitionKey": PARTITION_KEY, "RowKey": ROW_KEY, ROW_KEY: test_ts},
        UpdateMode.REPLACE,
    )
