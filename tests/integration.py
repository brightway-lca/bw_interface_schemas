from bw_interface_schemas import GraphLoader


def dump_graph(bike_as_graph):
    assert bike_as_graph.model_dump()


def construct_graph(bike_as_dict):
    assert GraphLoader(identifier_field="name").load(bike_as_dict, use_identifiers=True)
