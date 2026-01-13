"""
MetaBall Class.
"""


import time
import cv2
import yaml
from metaball.devices.camera import WebCamera
from metaball.modules.zmq import MetaBallPublisher
from metaball.models.onnx.ballnet import BallNet
from metaball.configs.deploy import CameraConfig, DeployConfig


class MetaBall:
    """
    MetaBall class.

    This class is used to initialize the metaball, camera, and BallNet model,
    and to run the metaball by capturing images and inferring the force and node
    displacement.

    Attributes:
        camera (WebCamera): The camera instance.
        ballnet (BallNet): The BallNet model instance.
        metaball_publisher (MetaBallPublisher): The MetaBall publisher instance.
    """

    def __init__(self, cfg: DeployConfig) -> None:
        """
        Initialize the metaball.

        Args:
            cfg (DeployConfig): The deployment configuration.
        """

        # Load the metaball parameters
        with open(cfg.camera_yaml, "r") as f:
            camera_params_dict = yaml.safe_load(f)

        camera_cfg = CameraConfig(**camera_params_dict)

        # Create a camera
        self.camera = WebCamera(camera_cfg)

        # Create a BallNet model
        self.ballnet = BallNet(cfg.onnx_path)

        # Create a metaball publisher
        self.metaball_publisher = MetaBallPublisher(host=cfg.host, port=cfg.port)

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