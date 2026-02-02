"""
Dataclass for model configuration parameters.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class ModelConfig:
    name: str = "BallNet"
    """Model name"""

    x_dim: Tuple[int, ...] = (6,)
    """Input dimension"""

    y_dim: Tuple[int, ...] = (6, 2931)
    """Output dimension"""

    hidden_dim: Tuple[Tuple[int, ...], ...] = (
        (512, 512),
        (1024, 1024),
    )
    """Hidden layer dimensions for each part of the model."""
