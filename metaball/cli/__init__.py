"""
MetaBall CLI
========

MetaBall CLI is a command line interface for running the MetaBall.
It provides a simple way to start the MetaBall.

Usage
-----

To run the MetaBall, use the following command:

```
run-metaball --name <metaball_name>
```

Where `<metaball_name>` is the name of the metaball configuration file (without the `.yaml` extension).
"""

from .run import main as run_metaball