# bw_interface_schemas

[![PyPI](https://img.shields.io/pypi/v/bw_interface_schemas.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/bw_interface_schemas.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/bw_interface_schemas)][pypi status]
[![License](https://img.shields.io/pypi/l/bw_interface_schemas)][license]

[![Read the documentation at https://bw_interface_schemas.readthedocs.io/](https://img.shields.io/readthedocs/bw_interface_schemas/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/brightway-lca/bw_interface_schemas/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/brightway-lca/bw_interface_schemas/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/bw_interface_schemas/
[read the docs]: https://bw_interface_schemas.readthedocs.io/
[tests]: https://github.com/brightway-lca/bw_interface_schemas/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/brightway-lca/bw_interface_schemas
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

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


## Building the Documentation

You can build the documentation locally by installing the documentation Conda environment:

```bash
conda env create -f docs/environment.yml
```

activating the environment

```bash
conda activate sphinx_bw_interface_schemas
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```