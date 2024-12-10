import json
import re
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, Literal, Self, Union

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

Identifier = Annotated[int | str, Field()]


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
    """
    The built-in node types. These are sufficient to describe standard life
    cycle assessment, but you can use custom types for new `Node` classes if
    needed.
    """

    project = "project"
    product_system = "product_system"
    process = "process"
    product = "product"
    elementary_flow = "elementary_flow"
    impact_assessment_method = "impact_assessment_method"
    impact_category = "impact_category"
    normalization = "normalization"
    weighting = "weighting"


class Node(Parsimonius):
    """
    Base class for nodes in the graph. Can include processes, products, and
    elementary flows, but also LCIA objects, and organizational tools like
    product systems and projects.

    All nodes must have a name and a type.
    """

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

    Collections can be nested. For example, a product system collection can
    belong to a project collection.
    """


class Project(Collection):
    """
    A set of `ProductSystem` and `ImpactAssessmentMethod` collections which
    encapsulate a sustainability assessment project. Projects can be
    self-contained, or can link to other `Project` collections.
    """

    node_type: Literal[NodeTypes.project] = NodeTypes.project


class ProductSystem(Collection):
    """
    A collection of unit processes with elementary and product flows,
    performing one or more defined functions, and which models the life cycle
    of a product. From ISO 14040.
    """

    license: str
    node_type: Literal[NodeTypes.product_system] = NodeTypes.product_system
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
    """
    Common base class for inventory nodes. Please only use subclasses of this
    node.
    """

    location: str | None = None
    references: list[DataSource] | None = None
    # Properties are quantitative but can be in a nested structure like
    # `{"a": {"amount": 7}}`
    properties: dict[str, JsonValue] | None = None


class Process(InventoryNode):
    """
    The smallest element considered in the life cycle inventory analysis for
    which input and output data are quantified. From ISO 14040.

    Can have one or more functional product edges. Multfunctional processes
    still have the type `NodeTypes.process`.

    Processes extend `InventoryNode` with a required `location` (string).
    """

    node_type: Literal[NodeTypes.process] = NodeTypes.process
    location: str
    # TBD: Time range?


class Product(InventoryNode):
    """
    Any good or service. From ISO 14040.

    Products extend `InventoryNode` with a required `unit` - this unit is the
    default used for every edge consuming or producing this product.

    The functional unit of sustainability assessment is always product(s).
    """

    node_type: Literal[NodeTypes.product] = NodeTypes.product
    unit: str


class ElementaryFlow(InventoryNode):
    """
    A material or energy entering the system being studied that has been drawn
    from the environment without previous human transformation, or material or
    energy leaving the system being studied that is released into the
    environment without subsequent human transformation. From ISO 14040.

    For sustainability assessment, an elementary flow is a concept (e.g. CO2)
    situated in a context (e.g. emission to air). The same underlying concept
    (e.g. CO2) can be both a product and an elementary flow, but because they
    operate in different contexts they are separate objects.

    Elementary flows extend `InventoryNode` with a required `unit` - this unit
    is the default used for every edge consuming or producing this product.
    They also require a `context`, which is a list of strings.
    """

    node_type: Literal[NodeTypes.elementary_flow] = NodeTypes.elementary_flow
    unit: str
    context: list[str]


class ImpactCategory(Node):
    """
    A class representing environmental issues of concern to which life cycle
    inventory analysis results may be assigned. From ISO 14040.

    In practical terms characterization is a list of factors (midpoint or
    endpoint) associated with elementary flows. This class stores metadata
    about normalization.this groups characterization factors  of the same
    category.
    """

    node_type: Literal[NodeTypes.impact_category] = NodeTypes.impact_category
    name: list[str]
    unit: str


class Normalization(Node):
    """
    Normalization is the calculation of the magnitude of the category indicator
    results relative to some reference information. The aim of the
    normalization is to understand better the relative magnitude for each
    indicator result of the product system under study. From ISO 14044.

    In practical terms normalization is a list of factors associated with
    elementary flows. This class stores metadata about normalization.
    """

    node_type: Literal[NodeTypes.normalization] = NodeTypes.normalization
    name: list[str]
    unit: str


class Weighting(Node):
    """
    Weighting is the process of converting indicator results of different
    impact categories by using numerical factors based on value-choices. It may
    include aggregation of the weighted indicator results. From ISO 14044.

    In practical terms weighting is a single factor associated with a
    normalization or characterization set. This class stores metadata about
    weighting.
    """

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
    source: Identifier
    target: Identifier
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


class NormalizationQuantitativeEdge(QuantitativeEdge):
    """"""

    edge_type: Literal[QuantitativeEdgeTypes.normalization]


class WeightingQuantitativeEdge(QuantitativeEdge):
    """"""

    edge_type: Literal[QuantitativeEdgeTypes.weighting] = (
        QuantitativeEdgeTypes.weighting
    )


class BiosphereQuantitativeEdge(QuantitativeEdge):
    edge_type: Literal[QuantitativeEdgeTypes.biosphere] = (
        QuantitativeEdgeTypes.biosphere
    )

    @model_validator(mode="before")
    @classmethod
    def not_functional(cls, data):
        assert "functional" not in data, "biosphere edges can never be functional"
        return data


class TechnosphereQuantitativeEdge(QuantitativeEdge):
    functional: bool = False
    edge_type: Literal[QuantitativeEdgeTypes.technosphere] = (
        QuantitativeEdgeTypes.technosphere
    )


if __name__ == "__main__":
    hiss = lambda name: re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    dirpath = Path(__file__).parent / "json_schema"
    objects = [
        BiosphereQuantitativeEdge,
        CharacterizationQuantitativeEdge,
        ProductSystem,
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
