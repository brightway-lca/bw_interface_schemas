"""bw_interface_schemas."""

__all__ = (
    "__version__",
    "ProcessWithReferenceProduct",
    "ElementaryFlow",
    "Node",
    "Process",
    "Product",
    "Source",
)

__version__ = "0.0.1"


from .lci import (
    ProcessWithReferenceProduct,
    ElementaryFlow,
    Node,
    Process,
    Product,
    Source,
)
