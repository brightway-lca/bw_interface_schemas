from typing import Optional

from pydantic import BaseModel, ConfigDict, JsonValue
from datetime import datetime


class Parsimonius(BaseModel):
    """Change defaule `model_dump` behaviour to not export unset values by default"""

    def model_dump(self, exclude_unset=True, *args, **kwargs):
        return super().model_dump(*args, exclude_unset=exclude_unset, **kwargs)


class Source(Parsimonius):
    """A data source, such as a publication or field measurement.

    Very preliminary."""

    authors: list[str]
    year: int
    title: str
    doi: Optional[str] = None


class Edge(Parsimonius):
    """An quantitative edge linking two nodes in the graph."""
    source: 'Node'
    target: 'Node'
    amount: float
    uncertainty_type: Optional[int] = None
    loc: Optional[float] = None
    scale: Optional[float] = None
    shape: Optional[float] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    negative: Optional[bool] = None


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
    type: Optional[str] = None
    comment: Optional[str | dict[str, str]] = None
    filename: Optional[str] = None
    references: Optional[list[Source]] = None
    # Was previously classifications - we want a more generic categorical set
    tags: Optional[dict[str, JsonValue]] = None
    exchanges: list[Edge] = []

    model_config = ConfigDict(
        extra="allow",
    )


class Process(Node):
    """A generic process, possibly multi-functional. Does not have a reference product.

    Only difference from `Node` is that some more fields are required."""

    name: str
    unit: str
    location: str
    # TBD: Time range?


class CombinedProcessWithReferenceProduct(Process):
    """Chimaera which serves as both a product and a process in the graph."""

    # Was previously "reference product", need the underscore here
    reference_product: str
    # Optional name for the amount of reference product produced.
    # Duplicates information in the exchanges.
    # Should be net amount.
    production_amount: Optional[float] = None


class Product(Node):
    name: str
    unit: str
    # Some products are the same globally, other have specific local properties
    location: Optional[str] = None
    properties: list  # TBD


class ElementaryFlow(Node):
    # Should be context, this is for backwards compatibility
    categories: list[str]
    name: str
    unit: str
