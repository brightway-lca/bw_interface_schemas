"""Fixtures for bw_interface_schemas"""

import pytest


@pytest.fixture
def process():
    return {
        'name': 'the name',
    }