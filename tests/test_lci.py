import pytest
from pydantic import ValidationError

from bw_interface_schemas import Node, Process


def test_unit_process_name_none(basic_lci_as_dict):
    lci = basic_lci_as_dict
    lci["name"] = None
    with pytest.raises(ValidationError) as err:
        Process(**lci)

    assert err.value.errors()[0]["msg"] == "Input should be a valid string"
    assert err.value.errors()[0]["loc"] == ("name",)


def test_unit_process_name_missing(basic_lci_as_dict):
    lci = basic_lci_as_dict
    del lci["name"]
    with pytest.raises(ValidationError) as err:
        Process(**lci)

    assert err.value.errors()[0]["msg"] == "Field required"
    assert err.value.errors()[0]["loc"] == ("name",)


def test_node_int_comment(basic_node_as_dict):
    node = basic_node_as_dict
    node["comment"] = 22
    with pytest.raises(ValidationError) as err:
        Node(**node)
    assert err.value.errors()[0]["msg"] == "Input should be a valid string"
    assert err.value.errors()[0]["loc"] == ("comment", "str")


def test_node_list_comment(basic_node_as_dict):
    node = basic_node_as_dict
    node["comment"] = [("🌸", "Benédiction"), ("💮", "L'Albatros")]

    with pytest.raises(ValidationError) as err2:
        Node(**node)
    assert err2.value.errors()[0]["msg"] == "Input should be a valid string"
    assert err2.value.errors()[0]["loc"] == ("comment", "str")


def test_node_dict_str_str_comment(basic_node_as_dict):
    node = basic_node_as_dict
    node["comment"] = {"🌸": "Benédiction", "💮": "L'Albatros"}
    Node(**node)


def test_node_dict_comment(basic_node_as_dict):
    node = basic_node_as_dict
    node["comment"] = {22: "Benédiction", ("b", "f"): "L'Albatros"}
    with pytest.raises(ValidationError) as err2:
        Node(**node)
    assert err2.value.errors()[0]["msg"] == "Input should be a valid string"
    assert err2.value.errors()[0]["loc"] == ("comment", "str")
