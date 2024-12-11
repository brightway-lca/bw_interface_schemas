from copy import deepcopy
from typing import Any, Self

from pydantic import BaseModel, model_validator

from bw_interface_schemas.models import (
    BiosphereQuantitativeEdge,
    CharacterizationQuantitativeEdge,
    Database,
    Edge,
    ElementaryFlow,
    Identifier,
    ImpactAssessmentMethod,
    ImpactCategory,
    Node,
    NodeTypes,
    Normalization,
    NormalizationQuantitativeEdge,
    Process,
    Product,
    ProductSystem,
    Project,
    QualitativeEdge,
    QualitativeEdgeTypes,
    QuantitativeEdgeTypes,
    TechnosphereQuantitativeEdge,
    Weighting,
    WeightingQuantitativeEdge,
)

NODE_MAPPING = {
    "project": Project,
    "product_system": ProductSystem,
    "process": Process,
    "product": Product,
    "elementary_flow": ElementaryFlow,
    "impact_assessment_method": ImpactAssessmentMethod,
    "impact_category": ImpactCategory,
    "normalization": Normalization,
    "weighting": Weighting,
}
EDGE_MAPPING = {
    "belongs_to": QualitativeEdge,
    "technosphere": TechnosphereQuantitativeEdge,
    "biosphere": BiosphereQuantitativeEdge,
    "characterization": CharacterizationQuantitativeEdge,
    "weighting": WeightingQuantitativeEdge,
    "normalization": NormalizationQuantitativeEdge,
}


def getter(obj: Any, attr: str) -> Any:
    """Retrieve `obj.attr` or `obj[attr]`"""
    if hasattr(obj, attr):
        return getattr(obj, attr)
    return obj.get(attr)


class Graph(BaseModel):
    """
    A `Graph` is the complete set of data used for sustainability assessment.
    This can include inventory and impact assessment data, and any other nodes
    and edges deemed useful by the practitioner to describe or model product
    systems and their effects.
    """

    nodes: dict[Identifier, Node]
    edges: list[Edge]

    @model_validator(mode="after")
    def edges_reference_nodes(self) -> Self:
        for edge in self.edges:
            if edge.source not in self.nodes:
                raise ValueError(f"Can't find edge source in nodes: {edge.source}")
            if edge.target not in self.nodes:
                raise ValueError(f"Can't find edge target in nodes: {edge.target}")
        return self

    def _objects_linked_to_product_system(self, label: str) -> None:
        objects = (
            identifier
            for identifier, node in self.nodes.items()
            if node.node_type == getattr(NodeTypes, label)
        )
        product_systems = {
            identifier
            for identifier, node in self.nodes.items()
            if node.node_type == NodeTypes.product_system
        }

        for obj in objects:
            if not any(
                edge.source == obj
                and edge.target in product_systems
                and edge.edge_type == QualitativeEdgeTypes.belongs_to
                for edge in self.edges
            ):
                raise ValueError(f"{label} node not linked to a product system: {obj}")

    @model_validator(mode="after")
    def processes_in_product_system(self) -> Self:
        self._objects_linked_to_product_system(label=NodeTypes.process)
        return self

    @model_validator(mode="after")
    def products_in_product_system(self) -> Self:
        self._objects_linked_to_product_system(label=NodeTypes.product)
        return self

    @model_validator(mode="after")
    def elementary_flows_in_product_system(self) -> Self:
        self._objects_linked_to_product_system(label=NodeTypes.elementary_flow)
        return self

    @model_validator(mode="after")
    def process_has_at_least_one_functional_edge(self) -> Self:
        processes = {
            identifier
            for identifier, node in self.nodes.items()
            if node.node_type == NodeTypes.process
        }

        for process in processes:
            if not any(
                (edge.source == process or edge.target == process)
                and edge.edge_type == QuantitativeEdgeTypes.technosphere
                and edge.functional
                for edge in self.edges
            ):
                raise ValueError(
                    f"Can't find functional edge for process node: {process}"
                )
        return self

    # TBD: LCIA associations

    @model_validator(mode="after")
    def biosphere_edge_source_target_types(self) -> Self:
        for edge in filter(
            lambda x: getter(x, "edge_type") == QuantitativeEdgeTypes.biosphere,
            self.edges,
        ):
            if not (
                getter(self.nodes[edge.source], "node_type") == NodeTypes.process
                and getter(self.nodes[edge.target], "node_type")
                == NodeTypes.elementary_flow
            ) or (
                getter(self.nodes[edge.target], "node_type") == NodeTypes.process
                and getter(self.nodes[edge.source], "node_type")
                == NodeTypes.elementary_flow
            ):
                raise ValueError(
                    f"Biosphere edges must link a process to an elementary flow ({edge})"
                )
        return self

    @model_validator(mode="after")
    def weighting_edge_source_target_types(self) -> Self:
        for edge in filter(
            lambda x: getter(x, "edge_type") == QuantitativeEdgeTypes.weighting,
            self.edges,
        ):
            if not getter(
                self.nodes[edge.source], "node_type"
            ) == NodeTypes.weighting and getter(
                self.nodes[edge.target], "node_type"
            ) in (NodeTypes.normalization, NodeTypes.impact_category):
                raise ValueError(
                    f"Weighting edges must link a weighting set to an impact category or a normalization set ({edge})"
                )
        return self

    @model_validator(mode="after")
    def normalization_edge_source_target_types(self) -> Self:
        for edge in filter(
            lambda x: getter(x, "edge_type") == QuantitativeEdgeTypes.normalization,
            self.edges,
        ):
            if not (
                getter(self.nodes[edge.source], "node_type")
                == NodeTypes.elementary_flow
                and getter(self.nodes[edge.target], "node_type")
                == NodeTypes.normalization
            ):
                raise ValueError(
                    "Normalization edges must link an elementary flow to a normalization set"
                )
        return self

    @model_validator(mode="after")
    def characterization_edge_source_target_types(self) -> Self:
        for edge in filter(
            lambda x: getter(x, "edge_type") == QuantitativeEdgeTypes.characterization,
            self.edges,
        ):
            if not (
                getter(self.nodes[edge.source], "node_type")
                == NodeTypes.elementary_flow
                and getter(self.nodes[edge.target], "node_type")
                == NodeTypes.impact_category
            ):
                raise ValueError(
                    "Characterization edges must link an elementary flow to an impact category"
                )
        return self

    @model_validator(mode="after")
    def technosphere_edge_must_specify_functionality(self) -> Self:
        for edge in filter(
            lambda x: getter(x, "edge_type") == QuantitativeEdgeTypes.technosphere,
            self.edges,
        ):
            if not isinstance(getter(edge, "functional"), bool):
                raise ValueError(
                    f"Technosphere edges must indicate functionality status ({edge})"
                )
        return self

    @model_validator(mode="after")
    def technosphere_edge_source_target_types(self) -> Self:
        for edge in filter(
            lambda x: getter(x, "edge_type") == QuantitativeEdgeTypes.technosphere,
            self.edges,
        ):
            if not (
                (
                    getter(self.nodes[edge.source], "node_type") == NodeTypes.process
                    and getter(self.nodes[edge.target], "node_type")
                    == NodeTypes.product
                )
                or (
                    getter(self.nodes[edge.target], "node_type") == NodeTypes.process
                    and getter(self.nodes[edge.source], "node_type")
                    == NodeTypes.product
                )
            ):
                raise ValueError(
                    f"Technosphere edges must link a process and a product ({edge})"
                )
        return self


def load_graph(
    graph: dict[str, list | dict],
    node_mapping: dict[str, Node] = NODE_MAPPING,
    edge_mapping: dict[str, Edge] = EDGE_MAPPING,
) -> Graph:
    """
    Load `graph` as simple Python objects into Pydantic classes.

    Intended for validation.

    Parameters
    ----------
    graph
        Graph as dictionary: `{"nodes": {<identifier>: <node_dict>}, "edges": [<edge_dicts>]}`.

    """
    node_mapping = node_mapping or NODE_MAPPING
    edge_mapping = edge_mapping or EDGE_MAPPING

    return Graph(
        nodes={
            key: node_mapping.get(obj["node_type"], Node)(**obj)
            for key, obj in graph["nodes"].items()
        },
        edges=[
            edge_mapping.get(obj["edge_type"], Edge)(**obj) for obj in graph["edges"]
        ],
    )
