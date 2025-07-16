#!/usr/bin/env python

"""
BallNet Inference

BallNet is a neural network model for infering the proprioception of the metaball.
The input is the motion, and the output is the force on the bottom surface and the displacement of mesh nodes.
The model is implemented in PyTorch and exported to ONNX format for inference.

Example usage:
```bash
python ballnet.py --name BallNet --model_path ./models/BallNet.onnx
```

For more information, please refer to https://github.com/han-xudong/metaball
"""

import argparse
from typing import Tuple
import numpy as np
from metaball.utils.nn_utils import init_model
from metaball.config import BallNetConfig


class BallNet:
    """
    BallNet class.

    This class is used to load the BallNet model and perform inference.
    The model is loaded using ONNX Runtime.

    Attributes:
        name (str): The name of the model.
        model_path (str): The path to the model file.
    """

    def __init__(self, ballnet_cfg: BallNetConfig) -> None:
        """
        BallNet initialization.

        Args:
            ballnet_cfg (BallNetConfig): The configuration for the BallNet model.
        """

        # Set the name and model path
        self.name = ballnet_cfg.name
        self.model_path = ballnet_cfg.model_path

        # Create a ONNX runtime model
        try:
            self.model = init_model(self.model_path, ballnet_cfg.device)
        except Exception as e:
            raise ValueError(f"Failed to load the model: {e}")

        # Print the initialization message
        print("{:-^80}".format(f" {self.name} Initialization "))
        print("Model Path:", self.model_path)
        print(
            "Input:",
            [f"{input.name} ({input.shape[0]}, {input.shape[1]})" for input in self.model.get_inputs()],
        )
        print(
            "Output:",
            [f"{output.name} ({output.shape[0]}, {output.shape[1]})" for output in self.model.get_outputs()],
        )
        print("Model Initialization Done.")
        print("{:-^80}".format(""))

    def infer(self, motion: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Inference.

        Args:
            motion (numpy.ndarray): The motion of the Ball.

        Returns:
            inference (tuple): Inference results.
                - force (numpy.ndarray): The force on the bottom surface of the Ball.
                - node (numpy.ndarray): The node displacement of the Ball.
        """

        return self.model.run(None, {"motion": motion.astype(np.float32).reshape(1, -1)})


if __name__ == "__main__":
    # Parse the arguments
    parser = argparse.ArgumentParser(description="BallNet inference.")
    parser.add_argument(
        "--name",
        type=str,
        default="BallNet",
        help="The name of the model.",
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="./models/BallNet.onnx",
        help="The path of the model.",
    )
    args = parser.parse_args()

    # Initialize the BallNet
    ballnet_cfg = BallNetConfig(name=args.name, model_path=args.model_path)

    ballnet = BallNet(ballnet_cfg)
