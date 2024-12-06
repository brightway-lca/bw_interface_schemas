from copy import deepcopy
from typing import Any, Self

from pydantic import BaseModel, model_validator

from bw_interface_schemas.models import (
    BiosphereQuantitativeEdge,
    CharacterizationQuantitativeEdge,
    Database,
    Edge,
    ElementaryFlow,
    ImpactAssessmentMethod,
    ImpactCategory,
    Node,
    NodeTypes,
    Normalization,
    NormalizationQuantitativeEdge,
    Process,
    Product,
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
    "database": Database,
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


class Graph(BaseModel):
    nodes: list[Node]
    edges: list[Edge]

    @model_validator(mode="after")
    def edges_reference_nodes(self) -> Self:
        for edge in self.edges:
            if not any(edge.source == node for node in self.nodes):
                raise ValueError(f"Can't find edge source in nodes: {edge.source}")
            if not any(edge.target == node for node in self.nodes):
                raise ValueError(f"Can't find edge target in nodes: {edge.target}")
        return self

    def _objects_linked_to_database(self, label: str) -> None:
        objects = (
            node for node in self.nodes if node.node_type == getattr(NodeTypes, label)
        )
        databases = [
            node for node in self.nodes if node.node_type == NodeTypes.database
        ]

        for obj in objects:
            if not any(
                edge.source == obj
                and edge.target == d
                and edge.edge_type == QualitativeEdgeTypes.belongs_to
                for edge in self.edges
                for d in databases
            ):
                raise ValueError(f"{label} node not linked to a database: {obj}")

    @model_validator(mode="after")
    def processes_in_database(self) -> Self:
        self._objects_linked_to_database(label=NodeTypes.process)
        return self

    @model_validator(mode="after")
    def products_in_database(self) -> Self:
        self._objects_linked_to_database(label=NodeTypes.product)
        return self

    @model_validator(mode="after")
    def elementary_flows_in_database(self) -> Self:
        self._objects_linked_to_database(label=NodeTypes.elementary_flow)
        return self

    @model_validator(mode="after")
    def process_has_at_least_one_functional_edge(self) -> Self:
        processes = (node for node in self.nodes if node.node_type == NodeTypes.process)

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


class GraphLoader:
    def __init__(
        self,
        node_mapping: dict[str, Node] | None = None,
        edge_mapping: dict[str, Edge] | None = None,
        identifier_field: str | int = "identifier",
    ):
        self.node_mapping = node_mapping or NODE_MAPPING
        self.edge_mapping = edge_mapping or EDGE_MAPPING
        self.identifier_field = identifier_field

    def _hash_list(self, obj: Any) -> Any:
        """Translate lists to tuples if needed"""
        if isinstance(obj, list):
            return tuple(obj)
        return obj

    def load(self, graph: dict[str, list], use_identifiers: bool = False) -> Graph:
        """
        Load `graph` as simple Python objects into Pydantic classes.

        Intended for validation.

        Parameters
        ----------
        graph
            Graph as dictionary: `{"nodes": [<node_dicts>], "edges": [<edge_dicts>]}`.
        use_identifiers
            Fill up edges specified by only identifiers by substituting the
            complete `Node` objects.

        """
        # We need to transform objects to pydantic classes so copy to avoid
        # changing the input data
        graph = deepcopy(graph)
        if use_identifiers:
            mapping = {
                self._hash_list(obj[self.identifier_field]): obj
                for obj in graph["nodes"]
            }
            for edge in graph["edges"]:
                edge["source"] = mapping[self._hash_list(edge["source"])]
                edge["target"] = mapping[self._hash_list(edge["target"])]

        # Convert edge source and target objects from `dicts` to pydantic
        # `Node` instances
        for edge in graph["edges"]:
            edge["source"] = self.node_mapping.get(edge["source"]["node_type"], Node)(
                **edge["source"]
            )
            edge["target"] = self.node_mapping.get(edge["target"]["node_type"], Node)(
                **edge["target"]
            )

        return Graph(
            nodes=[
                self.node_mapping.get(obj["node_type"], Node)(**obj)
                for obj in graph["nodes"]
            ],
            edges=[
                self.edge_mapping.get(obj["edge_type"], Edge)(**obj)
                for obj in graph["edges"]
            ],
        )
