from bw_interface_schemas import load_graph


def test_dump_graph(bike_as_graph):
    assert bike_as_graph.model_dump()


def test_construct_graph(bike_as_dict):
    assert load_graph(bike_as_dict)
