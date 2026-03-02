"""
Dataclass for deploy configuration parameters.
"""

from dataclasses import dataclass, field
from .camera import CameraConfig


@dataclass
class DeployConfig:
    host: str = "127.0.0.1"
    """Host address for the publisher."""

    port: int = 6666
    """Port number for the publisher."""

    onnx_path: str = "./models/BallNet.onnx"
    """Path to the ONNX model file."""
    
    camera: CameraConfig = field(default_factory=CameraConfig)
