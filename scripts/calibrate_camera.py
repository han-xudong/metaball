# !/usr/bin/env python3

"""
Camera Calibration Script

This script captures images from a camera (USB or Web) and saves them for calibration.

Example for USB camera:

```bash
python calibrate_camera.py --mode usb --id <id> --width 320 --height 240
```

where `<id>` is the camera ID which is usually 0 for the first camera, and can also be found in `ls /dev/video*`.

Example for Web camera:

```bash
python calibrate_camera.py --mode web --host <host> --width 320 --height 240
```

where `<host>` is the host of the camera, which depends on your network configuration.

The script opens a window to display the frame from the camera.
You can press 'c' to capture the image, and press 'ESC' to quit capturing.
The captured images are saved in the `data/camera_calibration` directory.

It also provides an option to calibrate the camera using OpenCV or MATLAB after capturing the images.
If you choose OpenCV, it will prompt you to enter the chessboard size and square size.
Then it will perform camera calibration and display the camera matrix and distortion coefficients.
If you choose MATLAB, it will exit the script and you can use MATLAB with the saved images.
A MATLAB script is also provided in the `scripts` directory for saving the camera matrix and
distortion coefficients into a `.yaml` file.

The calibration results should be copied to the `config/camera` directory for further use.

For more information, please refer to https://github.com/asMagiClaw/meta-finger
"""

import argparse
import sys
import os
import cv2
import yaml
import zmq
import numpy as np
from metaball.modules.protobuf import cam_msg_pb2
from metaball.utils.camera_utils import calibrate_camera


def main(name: str, mode: str, id: int, host: str, width: int, height: int) -> None:
    """
    Main function to calibrate the camera.

    Args:
        name (str): The name of the camera.
        mode (str): The mode of the camera (usb or web).
        id (int): The ID of the USB camera.
        host (str): The host of the Web camera.
        width (int): The width of the image.
        height (int): The height of the image.
    """

    if mode == "usb":
        # Initialize the USB camera
        try:
            camera = cv2.VideoCapture(id)
        except Exception as e:
            print(f"\033[31mError initializing camera: {e}\033[0m")
            print("\033[31mPlease check the camera ID.\033[0m")
            sys.exit()
        camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Print camera information
        print("{:=^80}".format(" USB Camera Initialization "))
        print(f"ID: {id}")
        print(f"Width: {width}")
        print(f"Height: {height}")
        print("{:=^80}".format(""))
    elif mode == "web":
        # Initialize the Web camera
        try:
            context = zmq.Context()
            socket = context.socket(zmq.SUB)
            socket.connect(f"tcp://{host}:5555")
            socket.setsockopt_string(zmq.SUBSCRIBE, "")
        except Exception as e:
            print(f"\033[31mError initializing camera: {e}\033[0m")
            print("\033[31mPlease check the camera host.\033[0m")
            sys.exit()
        cam_msg = cam_msg_pb2.Camera()
        cam_msg.ParseFromString(socket.recv())
        img = cv2.imdecode(np.frombuffer(cam_msg.img, dtype=np.uint8), cv2.IMREAD_COLOR)

        # Print camera information
        print("{:=^80}".format(" Web Camera Initialization "))
        print(f"Host: {host}")
        print(f"Width: {img.shape[1]}")
        print(f"Height: {img.shape[0]}")
        print("{:=^80}".format(""))
    else:
        raise ValueError("Invalid mode.")

    # Create a window to display the camera feed
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, width, height)

    # Create a directory to save the images
    img_dir = os.path.join(
        "data",
        f"camera_calibration/{name.lower().replace(' ', '_')}_{width}x{height}",
    )
    os.makedirs(img_dir, exist_ok=True)

    # Start capturing images
    print("Press 'c' to capture the image.")
    print("Press 'ESC' to quit capturing.")
    count = 0
    while True:
        # Read the frame from the camera
        if mode == "usb":
            ret, img = camera.read()
        elif mode == "web":
            cam_msg.ParseFromString(socket.recv())
            img = cv2.imdecode(np.frombuffer(cam_msg.img, dtype=np.uint8), cv2.IMREAD_COLOR)

        # Display the frame
        cv2.imshow(name, img)

        # Check for key presses
        key = cv2.waitKey(1)
        if key == 27:
            # ESC key pressed, exit the loop
            break
        elif key == ord("c"):
            # 'c' key pressed, capture the image
            img_path = os.path.join(img_dir, f"{count}.jpg")
            cv2.imwrite(img_path, img)
            print(f"{count}.jpg saved.")
            count += 1

    # Close the camera
    if mode == "usb":
        camera.release()
    elif mode == "web":
        socket.close()
        context.term()

    # Close the OpenCV window
    cv2.destroyAllWindows()
    print("Camera calibration completed.")
    print(f"Images saved to {img_dir}.")

    # Ask the user if they want to calibrate the camera using OpenCV or MATLAB
    print("To calibrate the camera, MATLAB or OpenCV can be used.")
    print("To use OpenCV, press 'y'. The script will continue to calibrate the camera.")
    print("To use MATLAB, press 'n'. The script will exit, and you can use MATLAB with the saved images.")
    user_input = input("Use OpenCV? (y/n): ")

    # If the user chooses OpenCV, perform camera calibration
    if user_input == "y":
        # Set up OpenCV camera calibration parameters
        print("OpenCV camera calibration started.")
        print("Please select the chessboard size.")
        chess_size = input("Chessboard size (e.g., 12x9): ")
        chess_size = tuple(map(int, chess_size.split("x")))
        print("Please select the square size.")
        square_size = float(input("Square size (mm): "))

        # Load the images for calibration
        print("Loading images for calibration...")
        images = []
        for img_name in os.listdir(img_dir):
            img_path = os.path.join(img_dir, img_name)
            img = cv2.imread(img_path)
            images.append(img)

        # Find chessboard corners in the images
        print("Finding chessboard corners...")
        mtx, dist, rvecs, tvecs = calibrate_camera(images, chess_size=chess_size, square_size=square_size)

        # Print the calibration results
        print("Camera matrix:")
        print(mtx)
        print("Distortion coefficients:")
        print(dist)
        print("Rotation vectors:")
        print(rvecs)
        print("Translation vectors:")
        print(tvecs)
        print("OpenCV camera calibration completed.")

        # Ask the user if they want to save the camera matrix and distortion coefficients
        user_input = input("Save the camera matrix and distortion coefficients? (y/n): ")
        if user_input == "y":
            camera_dist = {
                "mtx": mtx.tolist(),
                "dist": dist.tolist(),
            }
            # Save the camera matrix and distortion coefficients to a YAML file
            with open(
                f"{img_dir}/{name.lower().replace(' ', '_')}_{width}x{height}.yaml",
                "w",
            ) as f:
                yaml.dump(camera_dist, f)
            print(
                f"Calibration results are saved in {img_dir}/{name.lower().replace(' ', '_')}_{width}x{height}.yaml."
            )


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Calibrate the camera.")
    parser.add_argument(
        "--name",
        type=str,
        default="camera",
        help="The name of the camera.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="web",
        help="The camera mode (usb or web).",
    )
    parser.add_argument(
        "--id",
        type=int,
        default=0,
        help="The ID of the USB camera.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="10.114.201.1",
        help="The host of the Web camera.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=320,
        help="The width of the image.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=240,
        help="The height of the image.",
    )
    args = parser.parse_args()

    main(args.name, args.mode, args.id, args.host, args.width, args.height)
    print("Camera calibration script finished.")
