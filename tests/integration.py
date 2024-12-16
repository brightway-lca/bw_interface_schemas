from copy import deepcopy

import bw_interface_schemas as schema
from bw_interface_schemas.graph import NODE_MAPPING, EDGE_MAPPING


def test_dump_graph(bike_as_graph):
    assert bike_as_graph.model_dump()


def test_construct_graph(bike_as_dict):
    graph = schema.graph_to_pydantic(bike_as_dict)

    for key, node in bike_as_dict["nodes"].items():
        assert isinstance(graph.nodes[key], NODE_MAPPING[node["node_type"]])
        assert graph.nodes[key].name == node["name"]

    for kls, dct in zip(graph.edges, bike_as_dict["edges"]):
        assert isinstance(kls, EDGE_MAPPING[dct["edge_type"]])


def test_roundtrip(bike_as_dict):
    assert schema.graph_to_pydantic(deepcopy(bike_as_dict)).model_dump(
        exclude_unset=True
    ) == deepcopy(bike_as_dict)
