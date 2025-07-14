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
import os
from typing import Tuple
import onnxruntime
import numpy as np

class BallNet:
    def __init__(self, name, model_path) -> None:
        """BallNet initialization.

        Args:
            name: The name of the model.
            model_path: The path of the model.
        """
        
        # Set the name and model path
        self.name = name
        self.model_path = model_path
        if not self.model_path.endswith(".onnx"):
            raise ValueError("\033[31mThe model path must end with .onnx\033[0m")
        if not os.path.exists(self.model_path):
            raise ValueError("\033[31mThe model path does not exist\033[0m")
        
        # Create a ONNX runtime session
        self.session = onnxruntime.InferenceSession(self.model_path)
        
        # Print the initialization message
        print("{:-^80}".format(f" {self.name} Initialization "))
        print("Model Path:", self.model_path)
        print("Input:", [f"{input.name} ({input.shape[0]}, {input.shape[1]})" for input in self.session.get_inputs()])
        print("Output:", [f"{output.name} ({output.shape[0]}, {output.shape[1]})" for output in self.session.get_outputs()])
        print("Model Initialization Done.")
        print("{:-^80}".format(""))
     
    def infer(self, motion: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Inference.

        Args:
            motion (np.ndarray): The motion of the Ball.
            
        Returns:
            force (np.ndarray): The force on the bottom surface of the Ball.
            node (np.ndarray): The node displacement of the Ball.
        """

        # Run the session
        outputs = self.session.run(None, {"motion": motion.astype(np.float32).reshape(1, -1)})
        
        # Return force and node 
        # Note: ONNX export in scripts/onnx_export.py defines output_index as [1, 2]
        # where index 1 is force and index 2 is node/shape
        return outputs[0], outputs[1]
    

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
    Ball_net = BallNet(args.name, args.model_path)
    
    # Given a random motion and infer the force and node
    print("Given a random motion and infer the force and node...")
    motion = np.concatenate([10*np.random.rand(1, 2), 3*np.random.rand(1, 1), 0.3*np.random.rand(1, 3)], axis=1)
    print("Motion:", motion)
    force, node = Ball_net.infer(motion)
    print("Force:", force)
    print("Node:", node)