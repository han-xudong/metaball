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

import time
import cv2
import yaml
from metaball.devices.camera.webcamera import WebCamera
from metaball.modules.zmq.metaball import MetaballPublisher
from metaball.models.onnx.ballnet import BallNet


class metaball:
    def __init__(self) -> None:
        """Initialize the metaball."""

        # Load the finger parameters
        with open("./configs/finger.yaml", "r") as f:
            finger_params = yaml.load(f.read(), Loader=yaml.Loader)

        # Load the camera parameters
        with open(finger_params["camera_params_path"], "r") as f:
            camera_params = yaml.load(f.read(), Loader=yaml.Loader)

        # Load the detector parameters
        with open("./configs/detector.yaml", "r") as f:
            detector_params = yaml.load(f.read(), Loader=yaml.Loader)

        # Create a camera
        self.camera = WebCamera(
            name="Camera",
            camera_params=camera_params,
            detector_params=detector_params,
        )

        # Create a BallNet model
        self.finger_net = BallNet(name="BallNet", model_path=finger_params["model_path"])

        # Create a finger publisher
        self.finger_publisher = MetaballPublisher(ip=finger_params["ip"], port=finger_params["port"])

    def release(self) -> None:
        """
        Release the camera and close the finger publisher.
        """

        # Release the camera
        self.camera.release()

        # Close the finger publisher
        self.finger_publisher.close()

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
                force, node = self.finger_net.infer(pose_euler)

                # Publish the message
                self.finger_publisher.publishMessage(
                    cv2.imencode(".jpg", img, jpeg_params)[1].tobytes(),
                    pose_euler,
                    force,
                    node,
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
    metaball = metaball()
    # Run the metaball
    metaball.run()
