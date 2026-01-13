#!/usr/bin/env python

"""
BallNet Inference

BallNet is a neural network model for infering the proprioception of the metaball.
The input is the motion, and the output is the force on the bottom surface and the displacement of mesh nodes.
The model is implemented in PyTorch and exported to ONNX format for inference.

Example usage:
```bash
python ballnet.py --onnx_path ./models/BallNet.onnx
```

For more information, please refer to https://github.com/han-xudong/metaball
"""

import argparse
from typing import Tuple
import numpy as np
from metaball.utils.nn_utils import init_model


class BallNet:
    """
    BallNet class.

    This class is used to load the BallNet model and perform inference.
    The model is loaded using ONNX Runtime.
    """

    def __init__(self, onnx_path: str) -> None:
        """
        BallNet initialization.

        Args:
            onnx_path (str): The path to the ONNX model file.
        """

        # Create a ONNX runtime model
        try:
            self.model = init_model(onnx_path)
        except Exception as e:
            raise ValueError(f"Failed to load the model: {e}")

        # Print the initialization message
        print("Model Path:", onnx_path)
        print(
            "Input:",
            [f"{input.name} ({input.shape[0]}, {input.shape[1]})" for input in self.model.get_inputs()],
        )
        print(
            "Output:",
            [f"{output.name} ({output.shape[0]}, {output.shape[1]})" for output in self.model.get_outputs()],
        )

    def infer(self, motion: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Inference.

        Args:
            motion (numpy.ndarray): The motion of the MetaBall.

        Returns:
            inference (tuple): Inference results.
                - force (numpy.ndarray): The force on the bottom surface of the MetaBall.
                - node (numpy.ndarray): The node displacement of the MetaBall.
        """

        return self.model.run(None, {"motion": motion.astype(np.float32).reshape(1, -1)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BallNet Inference")
    parser.add_argument(
        "--onnx_path",
        type=str,
        default="./models/BallNet.onnx",
        help="Path to the ONNX model file.",
    )
    args = parser.parse_args()

    # Create a BallNet model
    ballnet = BallNet(onnx_path=args.onnx_path)
