"""bw_interface_schemas."""

__all__ = (
    "__version__",
    "CombinedProcessWithReferenceProduct",
    "ElementaryFlow",
    "Node",
    "Process",
    "Product",
    "Source",
)

__version__ = "0.0.1"


from .lci import (
    CombinedProcessWithReferenceProduct,
    ElementaryFlow,
    Node,
    Process,
    Product,
    Source,
)
