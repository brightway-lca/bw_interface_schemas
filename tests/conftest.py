import pytest

import bw_interface_schemas as schema


@pytest.fixture
def bike_as_dict() -> dict:
    return {
        "nodes": [
            {
                "node_type": "database",
                "name": "bike_db",
                "license": "CC-BY",
            },
            {
                "node_type": "process",
                "name": "natural gas extraction",
                "location": "NO",
            },
            {
                "node_type": "product",
                "name": "natural gas",
                "unit": "MJ",
            },
            {
                "node_type": "process",
                "name": "carbon fibre production",
                "location": "DE",
            },
            {
                "node_type": "product",
                "name": "carbon fibre",
                "unit": "kg",
            },
            {
                "node_type": "process",
                "name": "bike manufacturing",
                "location": "DK",
            },
            {
                "node_type": "product",
                "name": "bicycle",
                "unit": "number",
            },
            {
                "node_type": "elementary_flow",
                "name": "CO2",
                "context": ["air"],
                "unit": "kg",
            },
            {
                "node_type": "impact_assessment_method",
                "name": "IPCC",
                "license": "CC-BY",
            },
            {
                "node_type": "impact_category",
                "name": ["IPCC", "100 years"],
                "unit": "kg CO2-eq.",
            },
        ],
        "edges": [
            {
                "edge_type": "belongs_to",
                "source": ["IPCC", "100 years"],
                "target": "IPCC",
            },
            {
                "edge_type": "characterization",
                "amount": 1.0,
                "source": "CO2",
                "target": ["IPCC", "100 years"],
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
def bike_as_graph() -> schema.Graph:
    db = schema.Database(name="bike", license="CC-BY")
    ng_extraction = schema.Process(name="natural gas extraction", location="NO")
    ng = schema.Product(name="natural gas", unit="MJ")
    cf_production = schema.Process(name="carbon fibre production", location="DE")
    cf = schema.Product(name="carbon fibre", unit="kg")
    bike_manufacture = schema.Process(name="bike manufacturing", location="DK")
    bike = schema.Product(name="bike", unit="bicycle")
    co2 = schema.ElementaryFlow(name="CO2", unit="kg", context=["air"])
    ipcc = schema.ImpactAssessmentMethod(name="IPCC", license="CC-BY")
    gwp = schema.ImpactCategory(name=["IPCC", "100 years"], unit="CO2-eq.")

    return schema.Graph(
        nodes=[
            db,
            ipcc,
            gwp,
            ng_extraction,
            ng,
            cf_production,
            cf,
            bike_manufacture,
            bike,
            co2,
        ],
        edges=[
            schema.QualitativeEdge(
                source=gwp,
                target=ipcc,
                edge_type=schema.QualitativeEdgeTypes.belongs_to,
            ),
            schema.CharacterizationQuantitativeEdge(source=co2, target=gwp, amount=1),
            schema.TechnosphereQuantitativeEdge(
                source=ng,
                target=cf_production,
                amount=237,
            ),
            schema.TechnosphereQuantitativeEdge(
                source=cf,
                target=bike_manufacture,
                amount=2.5,
            ),
            schema.BiosphereQuantitativeEdge(
                source=cf_production, target=co2, amount=26.6
            ),
            schema.TechnosphereQuantitativeEdge(
                source=ng_extraction,
                target=ng,
                amount=1,
                functional=True,
            ),
            schema.TechnosphereQuantitativeEdge(
                source=cf_production,
                target=cf,
                amount=1,
                functional=True,
            ),
            schema.TechnosphereQuantitativeEdge(
                source=bike_manufacture,
                target=bike,
                amount=1,
                functional=True,
            ),
        ]
        + [
            schema.QualitativeEdge(
                source=node, target=db, edge_type=schema.QualitativeEdgeTypes.belongs_to
            )
            for node in (
                ng_extraction,
                ng,
                cf_production,
                cf,
                bike_manufacture,
                bike,
                co2,
            )
        ],
    )
