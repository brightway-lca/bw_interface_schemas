import pytest

import bw_interface_schemas as schema


@pytest.fixture
def bike_as_dict() -> dict:
    return {
        "nodes": {
            "bike_db": {
                "node_type": "product_system",
                "name": "bike_db",
                "license": "CC-BY",
            },
            "natural gas extraction": {
                "node_type": "process",
                "name": "natural gas extraction",
                "location": "NO",
            },
            "natural gas": {
                "node_type": "product",
                "name": "natural gas",
                "unit": "MJ",
            },
            "carbon fibre production": {
                "node_type": "process",
                "name": "carbon fibre production",
                "location": "DE",
            },
            "carbon fibre": {
                "node_type": "product",
                "name": "carbon fibre",
                "unit": "kg",
            },
            "bike manufacturing": {
                "node_type": "process",
                "name": "bike manufacturing",
                "location": "DK",
            },
            "bicycle": {
                "node_type": "product",
                "name": "bicycle",
                "unit": "number",
            },
            "CO2": {
                "node_type": "elementary_flow",
                "name": "CO2",
                "context": ["air"],
                "unit": "kg",
            },
            "IPCC": {
                "node_type": "impact_assessment_method",
                "name": "IPCC",
                "license": "CC-BY",
            },
            "IPCC - 100 years": {
                "node_type": "impact_category",
                "name": ["IPCC", "100 years"],
                "unit": "kg CO2-eq.",
            },
        },
        "edges": [
            {
                "edge_type": "belongs_to",
                "source": "IPCC - 100 years",
                "target": "IPCC",
            },
            {
                "edge_type": "characterization",
                "amount": 1.0,
                "source": "CO2",
                "target": "IPCC - 100 years",
            },
            {
                "edge_type": "biosphere",
                "amount": 26.6,
                "source": "carbon fibre production",
                "target": "CO2",
            },
            {
                "edge_type": "technosphere",
                "amount": 1,
                "source": "bike manufacturing",
                "target": "bicycle",
                "functional": True,
            },
            {
                "edge_type": "technosphere",
                "amount": 1,
                "source": "natural gas extraction",
                "target": "natural gas",
                "functional": True,
            },
            {
                "edge_type": "technosphere",
                "amount": 1,
                "source": "carbon fibre production",
                "target": "carbon fibre",
                "functional": True,
            },
            {
                "edge_type": "technosphere",
                "amount": 237,
                "source": "natural gas",
                "target": "carbon fibre production",
            },
            {
                "edge_type": "technosphere",
                "amount": 2.5,
                "source": "carbon fibre",
                "target": "bike manufacturing",
            },
        ]
        + [
            {
                "edge_type": "belongs_to",
                "source": node,
                "target": "bike_db",
            }
            for node in (
                "natural gas extraction",
                "natural gas",
                "carbon fibre production",
                "carbon fibre",
                "bike manufacturing",
                "bicycle",
                "CO2",
            )
        ],
    }


@pytest.fixture
def bike_as_graph(bike_as_dict) -> schema.Graph:
    return schema.load_graph(bike_as_dict)
