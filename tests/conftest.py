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


@pytest.fixture
def bike_process():
    return {"name": "bike production", "code": "bike", "location": "DK", "unit": "bike"}


@pytest.fixture
def ng_process():
    return {
        "name": "natural gas production",
        "unit": "MJ",
        "location": "NO",
        "code": "ng",
        "database": "bikes",
    }


@pytest.fixture
def cf_process():
    return {
        "name": "carbon fibre production",
        "unit": "kg",
        "location": "DE",
        "code": "cf",
        "database": "bikes",
    }


@pytest.fixture
def basic_node_as_dict():
    return {"code": "simple code", "database": "les fleurs du mal"}
