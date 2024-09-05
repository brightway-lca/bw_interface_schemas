"""bw_interface_schemas."""

__all__ = (
    "__version__",
    "ProcessWithReferenceProduct",
    "ElementaryFlow",
    "Node",
    "Edge",
    "Process",
    "Product",
    "DataSource",
)

__version__ = "0.1.0"


from .lci import (
    DataSource,
    Edge,
    ElementaryFlow,
    Node,
    Process,
    ProcessWithReferenceProduct,
    Product,
)

