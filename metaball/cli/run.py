"""
Run MetaBall
========

This script is to run the MetaBall, capturing metaball's deformation and inferring the force and node
displacement using the trained model.

Usage
-----

To run the MetaBall, use the following command:

```
run-metaball --name <metaball_name>
```

Where `<metaball_name>` is the name of the metaball configuration file (without the `.yaml` extension).
"""

import argparse
from metaball import Metaball


def main():
    parser = argparse.ArgumentParser(description="Run MetaBall")
    parser.add_argument(
        "--name",
        type=str,
        default="metaball",
        required=True,
        help="Name of the metaball configuration file (without .yaml extension)",
    )
    args = parser.parse_args()

    metaball = Metaball.from_config(args.name)
    metaball.run()


if __name__ == "__main__":
    main()
