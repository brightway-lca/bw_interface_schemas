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

__version__ = "0.1.0"


from .lci import (
    ProcessWithReferenceProduct,
    ElementaryFlow,
    Node,
    Process,
    Product,
    Source,
)
