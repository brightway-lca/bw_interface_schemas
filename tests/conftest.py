"""Fixtures for bw_interface_schemas"""

import pytest


@pytest.fixture
def basic_lci_as_dict():
    return {
        # Process fields
        "name": "a process name",
        "unit": "a unit",
        "location": "a location",
        # Node fields
        "code": "a code",
        "database": "a database",
    }
