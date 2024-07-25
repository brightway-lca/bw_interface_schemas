import json
import re
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, JsonValue, Field
from datetime import datetime


class Parsimonius(BaseModel):
    """Change defaule `model_dump` behaviour to not export unset values by default"""

    model_config = ConfigDict(
        extra="allow",
    )

    def model_dump(self, exclude_unset=True, *args, **kwargs):
        return super().model_dump(*args, exclude_unset=exclude_unset, **kwargs)


class DataSource(Parsimonius):
    """A data source, such as a publication or field measurement.

    Very preliminary."""

    authors: list[str]
    year: int
    title: str
    doi: Optional[str] = None


class UncertaintyDistribution(Parsimonius):
    """Separate out the fields used in uncertainty distributions"""
    amount: float
    uncertainty_type: Optional[int] = None
    loc: Optional[float] = None
    scale: Optional[float] = None
    shape: Optional[float] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    negative: Optional[bool] = None


class Edge(UncertaintyDistribution):
    """An quantitative edge linking two nodes in the graph."""
    edge_type: str = Field(alias="type")
    source: 'Node'
    target: 'Node'
    # The people want freedom
    properties: dict[str, Union[float, int]]
    tags: Optional[dict[str, JsonValue]] = None


class Node(Parsimonius):
    # Combination of database and code uniquely identifies a node
    code: str
    database: str
    # Recommended labels for these attributes
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    name: Optional[str] = None
    unit: Optional[str] = None
    location: Optional[str] = None
    node_type: Optional[str] = Field(alias="type", default=None)
    # Comment can be a single string or something more structured.
    comment: Optional[str | dict[str, str]] = None
    filename: Optional[str] = None
    references: Optional[list[DataSource]] = None
    # Was previously classifications - we want something more generic
    # Tags are chosen from defined set of possibilities
    tags: Optional[dict[str, JsonValue]] = None
    exchanges: list[Edge] = []


class Process(Node):
    """A generic process, possibly multi-functional. Does not have a reference product.

    Only difference from `Node` is that some more fields are required."""

    name: str
    unit: str
    location: str
    # TBD: Time range?


class ProcessWithReferenceProduct(Process):
    """Chimaera which serves as both a product and a process in the graph."""

    # Use `ProcessWithReferenceProduct.model_dump(by_alias=True)`
    # to get a dictionary using the alias field
    reference_product: str = Field(alias="reference product")
    # Optional name for the amount of reference product produced.
    # Duplicates information in the exchanges.
    # Should be net amount.
    production_amount: Optional[float] = None
    # Properties for reference product
    properties: Optional[dict[str, Union[float, int]]] = None

    model_config = ConfigDict(
        populate_by_name=False,
    )


class Product(Node):
    name: str
    unit: str
    # Some products are the same globally, other have specific local properties
    location: Optional[str] = None
    # Properties are quantitative; use tags to choose from a set of possible values
    properties: dict[str, Union[float, int]]


class ElementaryFlow(Node):
    # Previously called categories in Brightway
    context: list[str]
    name: str
    unit: str


if __name__ == "__main__":
    hiss = lambda name: re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    dirpath = Path(__file__).parent / "json_schema"
    for cls in (ElementaryFlow, Product, ProcessWithReferenceProduct, Process, Node, Edge):
        with open(dirpath / (hiss(cls.__name__) + ".json"), "w") as f:
            json.dump(cls.model_json_schema(), f, indent=2, ensure_ascii=False)
