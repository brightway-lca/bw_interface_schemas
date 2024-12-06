# bw_interface_schemas

[![PyPI](https://img.shields.io/pypi/v/bw_interface_schemas.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/bw_interface_schemas.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/bw_interface_schemas)][pypi status]
[![License](https://img.shields.io/pypi/l/bw_interface_schemas)][license]

## About

`bw_interface_schemas` defines a set of [pydantic](https://docs.pydantic.dev/2.0/) classes which will be the fundamental data schema for Brightway Cloud, the next iteration of the Brightway LCA software ecosystem. These schemas provide clear and consistent graph-based interfaces between Brightway software libraries, and simplify and harmonize the way data was modeled and stored in Brightway.

We have chosen to model all data in a graph, as a list of nodes and edges. This includes inventory data, which models how processes consume and produce products to form supply chains. It also includes impact assessment, where elementary flows are linked to impact categories via characterization edges, and data organization. Now both projects and databases are also in the graph, and process and product nodes are linked to databases via `belongs_to` relationship edges.

## Example

Here is our standard bicycle production example in the new paradigm:

<img src="example.png">

You can see two ways of building this graph in code in `tests/conftest.py`.

## Comparison with Brightway2

These new interfaces break backwards compatibility. We do not take such steps lightly; these changes were necessary to include database, projects, and methods in the same data store as other nodes and edges, and to add sanity checks and simpler code paths to building correct supply chain models.

Our approach has the following advantages:

* Edge `source` and `target` attributes now correctly indicate direction. Previously production edges had the product being produced as an input. Similarly, elementary flows being emitted were still modeled as inputs.
* Removal of implicit production edges. These seemed like a convenience but ultimately led to many hacks and difficult to diagnose incorrect behaviour for users.
* Removal of edge `type` labels which were at best confusing and sometimes incorrect. Edges now have a small set of possible types which only indicates the matrix they can be used in, and explicit instead of implicit direction.
* Clear separation of processes and products. Processes can only consume and produce products, and vice-versa. The previous allowance of chimaera processes which acted as products made modelling of multifunctional processes difficult and error-prone.
* The single graph format with LCI and LCIA nodes can sensibly model impact assessment data. Previously impact assessment data had to pretend to be inventory databases in `bw2io`.
* A unified data format which is identical in Python and JSON. This makes serialization, database storage, and exchange across systems and languages much easier.
* Pydantic validation provides usable feedback and prevents data errors entering the database.

## Installation

You can install _bw_interface_schemas_ via [pip] from [PyPI]:

```console
$ pip install bw_interface_schemas
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [MIT license][License],
_bw_interface_schemas_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://bw_interface_schemas.readthedocs.io/en/latest/usage.html
[License]: https://github.com/brightway-lca/bw_interface_schemas/blob/main/LICENSE
[Contributor Guide]: https://github.com/brightway-lca/bw_interface_schemas/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/brightway-lca/bw_interface_schemas/issues
