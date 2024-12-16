from copy import deepcopy

from bw_interface_schemas import graph_to_pydantic


def test_dump_graph(bike_as_graph):
    assert bike_as_graph.model_dump()


def test_construct_graph(bike_as_dict):
    assert graph_to_pydantic(bike_as_dict)


def test_roundtrip(bike_as_dict):
    def add_default_fields(data: dict) -> dict:
        edge_fields = ("comment", "properties", "references", "tags")
        node_fields = ("comment", "tags")

        for node in data["nodes"].values():
            for field in node_fields:
                if field not in node:
                    node[field] = None
        for edge in data["edges"]:
            for field in edge_fields:
                if field not in edge:
                    edge[field] = None
        return data

    from pprint import pprint

    pprint(graph_to_pydantic(deepcopy(bike_as_dict)).edges[1])
    pprint(graph_to_pydantic(deepcopy(bike_as_dict)).model_dump()["edges"][1])
    pprint(add_default_fields(deepcopy(bike_as_dict))["edges"][1])

    assert graph_to_pydantic(deepcopy(bike_as_dict)).model_dump() == add_default_fields(
        deepcopy(bike_as_dict)
    )
