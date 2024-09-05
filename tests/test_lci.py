from pydantic import ValidationError
from bw_interface_schemas import Process
import pytest


def test_unit_process_name_none(basic_lci_as_dict):
    lci = basic_lci_as_dict
    lci['name'] = None
    with pytest.raises(ValidationError) as err:
        Process(**lci)

    assert err.value.errors()[0]['msg'] == 'Input should be a valid string'
    assert err.value.errors()[0]['loc'] == ('name',)


def test_unit_process_name_missing(basic_lci_as_dict):
    lci = basic_lci_as_dict
    del lci['name']
    with pytest.raises(ValidationError) as err:
        Process(**lci)

    assert err.value.errors()[0]['msg'] == 'Field required'
    assert err.value.errors()[0]['loc'] == ('name',)
