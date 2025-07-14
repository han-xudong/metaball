#!/usr/bin/env python

"""
ZMQ configuration
===

This module contains the configuration for the ZMQ publisher and subscriber.
"""

import os
import yaml
from typing import Optional


class ZMQConfig:
    """
    ZMQ configuration class.

    Attributes:
        claw_id (int): The ID of the claw.
        publish_host (str): The host address for the ZMQ connection.
        claw_port (int): The port for the claw connection.
        finger_0_port (int): The port for finger 0 connection.
        finger_1_port (int): The port for finger 1 connection.
        publish_port (int): The port for publishing data.
        phone_host (str): The host address of the phone.
        phone_port (int): The port for the phone connection.
        bilateral_host (str): The host address of the bilateral connection.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the ZMQ configuration.
        """

        self.publish_host = "0.0.0.0"

        self.publish_port = 5555

    def read_config_file(self, file_path: str, root_dir: str = ".") -> None:
        """
        Read the camera configuration from a yaml file.

        Args:
            file_path (str): The path to the yaml configuration file.
            root_dir (str): The root directory to resolve relative paths.
        """

        with open(os.path.join(root_dir, file_path), "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

            for key, value in config.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    def set_host(self, host: str) -> None:
        """
        Set the host address for the phone.

        Args:
            host (str): The host address.
        """
        
        self.host = host
