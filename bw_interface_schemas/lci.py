import json
import re
from pathlib import Path
from typing import Union

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
    doi: str | None = None


class UncertaintyDistribution(BaseModel):
    """Separate out the fields used in uncertainty distributions"""
    amount: float
    uncertainty_type: int | None = None
    loc: float | None = None
    scale: float | None = None
    shape: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    negative: bool | None = None


class Edge(Parsimonius):
    """An qualitative edge linking two nodes in the graph."""
    edge_type: str
    source: 'LCINode'
    target: 'LCINode'
    properties: dict[str, Union[float, int]]
    tags: dict[str, JsonValue] | None = None


class QuantitativeEdge(Edge, UncertaintyDistribution):
    """An quantitative edge linking two nodes in the graph."""
    edge_type: str
    source: 'LCINode'
    target: 'LCINode'
    properties: dict[str, Union[float, int]]
    tags: dict[str, JsonValue] | None = None


class LCINode(Parsimonius):
    # Recommended labels for these attributes
    name: str
    unit: str
    created: datetime | None = None
    modified: datetime | None = None
    location: str | None = None
    node_type: str | None = None
    # Comment can be a single string or something more structured.
    comment: Union[str, dict[str, str], None] = None
    references: list[DataSource] | None = None
    # Was previously classifications - we want something more generic
    # Tags are chosen from defined set of possibilities
    tags: dict[str, JsonValue] | None = None
    properties: dict[str, Union[float, int]]


class Process(LCINode):
    """A generic process, possibly multi-functional. Does not have a reference product.

    Only difference from `LCINode` is that some more fields are required."""
    location: str
    # TBD: Time range?


class Product(LCINode):
    pass


class ElementaryFlow(LCINode):
    # Previously called categories in Brightway
    context: list[str]


if __name__ == "__main__":
    hiss = lambda name: re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    dirpath = Path(__file__).parent / "json_schema"
    for cls in (ElementaryFlow, Product, Process, LCINode, QuantitativeEdge):
        with open(dirpath / (hiss(cls.__name__) + ".json"), "w") as f:
            json.dump(cls.model_json_schema(), f, indent=2, ensure_ascii=False)
