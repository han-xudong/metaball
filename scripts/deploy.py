#!/usr/bin/env python

"""
Deploy Script for MetaBall.

Usage:

```bash
python scripts/deploy.py
```

Various configuration options are available:
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
| Options       | Description                                   | Type   | Default                          |
|---------------|-----------------------------------------------|--------|----------------------------------|
| --host        | Host address for the publisher.               | str    | 127.0.0.1                        |
| --port        | Port number for the publisher.                | int    | 6666                             |
| --camera-yaml | Path to the camera configuration YAML file.   | str    | ./configs/maixcam-xxxx.yaml      |
| --onnx-path   | Path to the ONNX model file.                  | str    | ./models/BallNet.onnx            |
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────╯
"""

import tyro
from metaball import Metaball
from metaball.configs.deploy import DeployConfig

def main():
    cfg = tyro.cli(DeployConfig)

    metaball = Metaball(cfg=cfg)
    metaball.run()
    

if __name__ == "__main__":
    main()