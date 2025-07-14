#!/usr/bin/env python

"""
Metaball

This script is to run the Metaball, capturing metaball's deformation and
inferring the force and node displacement using the trained model.

Example usage:

```bash
python run_metaball.py --onnx_path <onnx_path>
```

where <onnx_path> is the path to the ONNX model file.
"""

import pathlib
import time
import cv2
import yaml
from metaball.devices.camera import WebCamera
from metaball.modules.zmq import MetaballPublisher
from metaball.models.onnx.ballnet import BallNet
from metaball.config import CameraConfig, BallNetConfig, ZMQConfig


class Metaball:
    def __init__(self) -> None:
        """
        Initialize the metaball.
        """

        print("{:=^80}".format(f" Metaball Initialization "))

        # Set root directory
        self.root_dir = pathlib.Path(__file__).parent.parent

        # Load the metaball parameters
        metaball_config_path = self.root_dir.joinpath("configs", "metaball.yaml")
        with metaball_config_path.open("r") as f:
            metaball_params = yaml.load(f.read(), Loader=yaml.Loader)

        # Load the camera parameters
        self.camera_cfg = CameraConfig()
        self.camera_cfg.read_config_file(pathlib.Path(metaball_params["camera"]), root_dir=str(self.root_dir))

        # Create a camera
        self.camera = WebCamera(
            name=f"camera",
            camera_cfg=self.camera_cfg,
        )

        # Create a BallNet model
        self.ballnet_cfg = BallNetConfig(model_path=str(self.root_dir.joinpath(pathlib.Path(metaball_params["ballnet"]))))
        self.ballnet = BallNet(self.ballnet_cfg)

        # Create a metaball publisher
        self.zmq_cfg = ZMQConfig()
        self.metaball_publisher = MetaballPublisher(
            host=self.zmq_cfg.publish_host, port=self.zmq_cfg.publish_port
        )

    def release(self) -> None:
        """
        Release the camera and close the metaball publisher.
        """

        # Release the camera
        self.camera.release()

        # Close the metaball publisher
        self.metaball_publisher.close()

    def run(self) -> None:
        """
        Run the metaball.
        """

        # Set the jpeg parameters
        jpeg_params = [cv2.IMWRITE_JPEG_QUALITY, 50]

        # Initialize the variables
        start_time = time.time()
        frame_count = 0

        # Start publishing
        try:
            while True:
                # Get the image and pose
                pose, img = self.camera.readImageAndPose()
                # Convert the pose to the reference pose
                pose_ref = self.camera.poseToReferece(pose)
                # Convert the pose from the marker frame to the camera frame
                pose_global = self.camera.poseAxisTransfer(pose_ref)
                # Convert the pose to the euler angles
                pose_euler = self.camera.poseVectorToEuler(pose_global)

                # Predict the force and node
                force, node = self.ballnet.infer(pose_euler)

                # Publish the message
                self.metaball_publisher.publishMessage(
                    cv2.imencode(".jpg", img, jpeg_params)[1].tobytes(),
                    pose_euler.flatten().tolist(),
                    force.flatten().tolist(),
                    node.flatten().tolist(),
                )

                frame_count += 1

                # Print the FPS
                if frame_count == 60:
                    print(f"FPS: %.2f" % (frame_count / (time.time() - start_time)))
                    start_time = time.time()
                    frame_count = 0
        except KeyboardInterrupt:
            print("Stopping the camera...")
        finally:
            # Release the metaball
            self.release()


if __name__ == "__main__":
    # Create a metaball instance
    metaball = Metaball()
    # Run the metaball
    metaball.run()
