import json
import re
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal, Self, Union

from pydantic import BaseModel, ConfigDict, JsonValue, model_validator


def getter(obj: Any, attr: str) -> Any:
    """Retrieve `obj.attr` or `obj[attr]`"""
    if hasattr(obj, attr):
        return getattr(obj, attr)
    return obj.get(attr)


class Parsimonius(BaseModel):
    """Change default `model_dump` behaviour to not export unset values by default"""

    model_config = ConfigDict(
        extra="allow",
    )

    def model_dump(self, exclude_unset=True, *args, **kwargs):
        return super().model_dump(*args, exclude_unset=exclude_unset, **kwargs)


class DataSource(Parsimonius):
    """
    A data source, such as a publication or field measurement.

    A very rough draft; expect changes.
    """

    authors: list[str]
    year: int
    title: str
    doi: str | None = None


class NodeTypes(StrEnum):
    project = "project"
    database = "database"
    process = "process"
    product = "product"
    elementary_flow = "elementary_flow"
    impact_assessment_method = "impact_assessment_method"
    impact_category = "impact_category"
    normalization = "normalization"
    weighting = "weighting"


class Node(Parsimonius):
    # Recommended labels for these attributes
    name: str
    node_type: NodeTypes | str
    # Comment can be a single string or something more structured.
    comment: Union[str, dict[str, str], None] = None
    # Was previously classifications - we want something more generic
    # Tags are chosen from defined set of possibilities
    tags: dict[str, JsonValue] | None = None


class Collection(Node):
    """
    A `Collection` is a group of nodes organized in a common container.

    These nodes can be part of inventory supply chains, impact assessment methods,
    parameterization sets, or any other logical unit of organization.

    `Collection` nodes are normally linked to other nodes via qualitative
    relationship edges, such as `EdgeTypes.belongs_to`.

    The edge type should clearly differentiate the intended edge direction. In
    this case, a `Product` node (source) `belongs_to` a `Collection`.

    Collections can be nested. For example, a database collection can belong to
    a project collection.
    """


class Project(Collection):
    """
    A set of `Database` and `ImpactAssessmentMethod` collections which
    encapsulate a sustainability assessment project. Projects can be
    self-contained, or can link to other `Project` collections.
    """

    node_type: Literal[NodeTypes.project] = NodeTypes.project


class Database(Collection):
    """
    A set of life cycle inventory nodes and edges which have a common label and
    license.
    """

    license: str
    node_type: Literal[NodeTypes.database] = NodeTypes.database
    references: list[DataSource] | None = None


class ImpactAssessmentMethod(Collection):
    """
    A set of impact categories, weightings, and normalizations, with their
    associated factors.
    """

    license: str
    node_type: Literal[NodeTypes.impact_assessment_method] = (
        NodeTypes.impact_assessment_method
    )
    references: list[DataSource] | None = None


class InventoryNode(Node):
    location: str | None = None
    references: list[DataSource] | None = None
    # Properties are quantitative but can be in a nested structure like
    # `{"a": {"amount": 7}}`
    properties: dict[str, JsonValue] | None = None


class Process(InventoryNode):
    """A generic process, possibly multi-functional. Does not have a reference product.

    Only difference from `LCINode` is that some fields are required."""

    node_type: Literal[NodeTypes.process] = NodeTypes.process
    location: str
    # TBD: Time range?


class Product(InventoryNode):
    node_type: Literal[NodeTypes.product] = NodeTypes.product
    unit: str


class ElementaryFlow(InventoryNode):
    node_type: Literal[NodeTypes.elementary_flow] = NodeTypes.elementary_flow
    unit: str
    context: list[str]


class ImpactCategory(Node):
    node_type: Literal[NodeTypes.impact_category] = NodeTypes.impact_category
    name: list[str]
    unit: str


class Normalization(Node):
    node_type: Literal[NodeTypes.normalization] = NodeTypes.normalization
    name: list[str]
    unit: str


class Weighting(Node):
    node_type: Literal[NodeTypes.weighting] = NodeTypes.weighting
    name: list[str]
    unit: str


class QualitativeEdgeTypes(StrEnum):
    belongs_to = "belongs_to"


class QuantitativeEdgeTypes(StrEnum):
    technosphere = "technosphere"
    biosphere = "biosphere"
    characterization = "characterization"
    weighting = "weighting"
    normalization = "normalization"


class Edge(Parsimonius):
    edge_type: str
    source: Node
    target: Node
    comment: Union[str, dict[str, str], None] = None
    references: list[DataSource] | None = None
    tags: dict[str, JsonValue] | None = None
    properties: dict[str, JsonValue] | None = None


class QualitativeEdge(Edge):
    """
    A qualitative edge linking two nodes in the graph.

    The type of relationship is defined by the `edge_type`. Normally these are
    drawn from `QualitativeEdgeTypes` but don't have to be.
    """

    edge_type: QualitativeEdgeTypes


class QuantitativeEdge(Edge):
    """An quantitative edge linking two nodes in the graph."""

    edge_type: QuantitativeEdgeTypes | str
    amount: float
    uncertainty_type: int | None = None
    loc: float | None = None
    scale: float | None = None
    shape: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    negative: bool | None = None


class CharacterizationQuantitativeEdge(QuantitativeEdge):
    """"""

    edge_type: Literal[QuantitativeEdgeTypes.characterization] = (
        QuantitativeEdgeTypes.characterization
    )
    location: str | None = None

    @model_validator(mode="after")
    def source_target_types(self) -> Self:
        if not (
            getter(self.source, "node_type") == NodeTypes.elementary_flow
            and getter(self.target, "node_type") == NodeTypes.impact_category
        ):
            raise ValueError(
                "Characterization edges must link an elementary flow to an impact category"
            )
        return self


class NormalizationQuantitativeEdge(QuantitativeEdge):
    """"""

    edge_type: Literal[QuantitativeEdgeTypes.normalization]

    @model_validator(mode="after")
    def source_target_types(self) -> Self:
        if not (
            getter(self.source, "node_type") == NodeTypes.elementary_flow
            and getter(self.target, "node_type") == NodeTypes.normalization
        ):
            raise ValueError(
                "Normalization edges must link an elementary flow to a normalization set"
            )
        return self


class WeightingQuantitativeEdge(QuantitativeEdge):
    """"""

    edge_type: Literal[QuantitativeEdgeTypes.weighting] = (
        QuantitativeEdgeTypes.weighting
    )

    @model_validator(mode="after")
    def source_target_types(self) -> Self:
        if not getter(self.source, "node_type") == NodeTypes.weighting and self.target[
            "node_type"
        ] in (NodeTypes.normalization, NodeTypes.impact_category):
            raise ValueError(
                "Weighting edges must link a weighting set to an impact category or normalization set"
            )
        return self


class BiosphereQuantitativeEdge(QuantitativeEdge):
    edge_type: Literal[QuantitativeEdgeTypes.biosphere] = (
        QuantitativeEdgeTypes.biosphere
    )

    @model_validator(mode="after")
    def source_target_types(self) -> Self:
        if not (
            getter(self.source, "node_type") == NodeTypes.process
            and getter(self.target, "node_type") == NodeTypes.elementary_flow
        ) or (
            getter(self.target, "node_type") == NodeTypes.process
            and getter(self.source, "node_type") == NodeTypes.elementary_flow
        ):
            raise ValueError(
                "Biosphere edges must link a process to an elementary flow"
            )
        return self

    @model_validator(mode="before")
    @classmethod
    def not_functional(cls, data):
        assert "functional" not in data, "biosphere edges can never be functional"
        return data


class TechnosphereQuantitativeEdge(QuantitativeEdge):
    """"""

    functional: bool = False
    edge_type: Literal[QuantitativeEdgeTypes.technosphere] = (
        QuantitativeEdgeTypes.technosphere
    )

    @model_validator(mode="after")
    def technosphere_edge_must_specify_functionality(self) -> Self:
        if not (
            (
                getter(self.source, "node_type") == NodeTypes.process
                and getter(self.target, "node_type") == NodeTypes.product
            )
            or (
                getter(self.target, "node_type") == NodeTypes.process
                and getter(self.source, "node_type") == NodeTypes.product
            )
        ):
            raise ValueError("Technosphere edges must link a process and a product")
        return self


if __name__ == "__main__":
    hiss = lambda name: re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    dirpath = Path(__file__).parent / "json_schema"
    objects = [
        BiosphereQuantitativeEdge,
        CharacterizationQuantitativeEdge,
        Database,
        DataSource,
        Edge,
        ElementaryFlow,
        ImpactAssessmentMethod,
        ImpactCategory,
        InventoryNode,
        Node,
        Normalization,
        NormalizationQuantitativeEdge,
        Process,
        Product,
        Project,
        QualitativeEdge,
        QuantitativeEdge,
        TechnosphereQuantitativeEdge,
        Weighting,
        WeightingQuantitativeEdge,
    ]
    for obj in objects:
        with open(dirpath / (hiss(obj.__name__) + ".json"), "w") as f:
            json.dump(obj.model_json_schema(), f, indent=2, ensure_ascii=False)
