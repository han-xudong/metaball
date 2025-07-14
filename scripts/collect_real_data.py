#!/usr/bin/env python

"""
Real Data Collection

This script is to collect real data of the finger, including the motion from the camera
and the force from the force/torque sensor, for training the model.
"""

import time
import yaml
import numpy as np
from pynput import keyboard
from multiprocessing import Queue, Process, Value
from pynetft import NetFT
from metaball.modules.zmq.finger import FingerPublisher
from metaball.devices.camera.webcamera import WebCamera
from metaball.utils.data_utils import save_data, force_sensor2global
from metaball.utils.camera_utils import img_encode


def read_data(queue, is_rec, should_stop) -> None:
    """
    Read data from the camera and the force/torque sensor, and publish the data.
    
    Args:
        queue (Queue): The queue to put the data into.
        is_rec (Value): The shared boolean flag to indicate if recording is enabled.
        should_stop (Value): The shared boolean flag to indicate if the process should stop.
    """

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
    camera = WebCamera(
        name="Camera",
        camera_params=camera_params,
        detector_params=detector_params,
    )

    # Create a finger publisher
    finger_publisher = FingerPublisher(ip=finger_params["ip"], port=finger_params["port"])

    # Load the force/torque sensor parameters
    with open("./configs/netft.yaml", "r") as f:
        netft_params = yaml.load(f.read(), Loader=yaml.Loader)

    # Create a NetFT object
    netft = NetFT(
        host=netft_params["host"],
        count_per_force=netft_params["count_per_force"],
        count_per_torque=netft_params["count_per_torque"],
    )

    # Connect to the FT sensor
    try:
        netft.connect()
    except Exception as e:
        raise RuntimeError(f"Failed to connect to the FT sensor: {e}")

    # Set the reference frame for the force/torque sensor
    s2g_tvec = np.array(netft_params["sensor2global"]["translation"])
    s2g_rmat = np.array(netft_params["sensor2global"]["rotation"])

    # Initialize variables
    force = np.zeros(6)
    start_time = time.time()
    frame_count = 0
    node = np.zeros(1800)

    # Start collecting data
    try:
        while True:
            # Get the image and pose
            pose, img = camera.readImageAndPose()
            # Convert the pose to the reference pose
            pose_ref = camera.poseToReferece(pose)
            # Convert the pose from the marker frame to the camera frame
            pose_global = camera.poseAxisTransfer(pose_ref)
            # Convert the pose to the euler angles
            pose_euler = camera.poseVectorToEuler(pose_global)

            # Get the force/torque data
            resp = netft.get_real_data()
            for i in range(6):
                force[i] = resp.FTData[i]
            # Convert the force to the global frame
            force = force_sensor2global(force, s2g_rmat, s2g_tvec)
            # Publish the message
            finger_publisher.pub_msg(
                img_encode(img),
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

            # Check if recording is enabled
            if is_rec.value:
                # Put the data in the queue
                try:
                    queue.put([pose_euler.flatten(), force, img], block=False)
                except Exception as e:
                    print(f"Error putting data in queue: {e}")

            # Check if the stop flag is set
            if should_stop.value:
                break
    except KeyboardInterrupt:
        should_stop.value = True
    finally:
        print("Stopping reading data...")
        # Disconnect the NetFT sensor
        netft.disconnect()
        # Release the camera
        camera.release()
        # Close the finger publisher
        finger_publisher.close()


def record_data(queue, is_rec, should_stop) -> None:
    """
    Record the data from the queue and save it to a file.

    Args:
        queue (Queue): The queue to get the data from.
        is_rec (Value): The shared boolean flag to indicate if recording is enabled.
        should_stop (Value): The shared boolean flag to indicate if the process should stop.
    """

    # Initialize variables
    count = 0
    recorded_data = None

    # Start recording data
    try:
        while True:
            # Check if recording is enabled
            if not is_rec.value and recorded_data is None:
                # Wait for the recording to start
                time.sleep(0.01)
                continue
            elif not is_rec.value and recorded_data is not None:
                # Stop recording
                print("Recording stopped in record_data process.")
                print(f"Recorded {count} frames.")
                # Save the data to files
                if count > 0:
                    data_dir = f"./data/real/{time.strftime('%Y%m%d_%H%M%S')}"
                    save_data(recorded_data, data_dir)
                recorded_data = None
                continue
            elif is_rec.value and recorded_data is None:
                # Start recording
                print("Recording started in record_data process.")
                recorded_data = []
                count = 0
            elif is_rec.value and recorded_data is not None:
                # Try to get data from the queue with a timeout
                try:
                    if not queue.empty():
                        data = queue.get(block=False)
                        recorded_data.append(data)
                        count += 1
                        if count % 60 == 0:
                            print(f"Recorded frames: {count}")
                    else:
                        # No data in queue, sleep a bit to prevent CPU hogging
                        time.sleep(0.01)
                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(0.01)

            # Check if the stop flag is set
            if should_stop.value:
                # Save any remaining data before exiting
                if recorded_data and len(recorded_data) > 0:
                    print(f"Saving {len(recorded_data)} frames before exit...")
                    save_data(recorded_data)
                break
    except KeyboardInterrupt:
        should_stop.value = True
    finally:
        print("Stopping recording data...")


def on_press(key, is_rec, should_stop):
    """
    Listener for the key press event.
    Press 'r' to start recording data.
    Press 's' to stop recording data.
    
    Args:
        key (Key): The key that was pressed.
        is_rec (Value): The shared boolean flag to indicate if recording is enabled.
        should_stop (Value): The shared boolean flag to indicate if the process should stop.
    """

    try:
        # Handle normal keys
        if key.char == "r":
            is_rec.value = True
            print("Recording flag set to True.")
        elif key.char == "s":
            is_rec.value = False
            print("Recording flag set to False.")
    except AttributeError:
        # Handle special keys
        pass

    if should_stop.value:
        # Stop the listener
        return False


def main() -> None:
    """
    Main function to run the data collection.
    """

    # Create shared variables for multiprocessing
    queue = Queue(maxsize=1000)  # Add a maximum size to prevent memory issues
    is_rec = Value("b", False)  # Shared boolean flag for recording
    should_stop = Value("b", False)  # Shared boolean flag for stopping

    # Create a process to read data from the camera and the force/torque sensor
    read_process = Process(target=read_data, args=(queue, is_rec, should_stop))
    read_process.daemon = True
    read_process.start()

    # Create a process to record data
    record_process = Process(target=record_data, args=(queue, is_rec, should_stop))
    record_process.daemon = True
    record_process.start()

    # Set up the keyboard listener with the shared variables
    listener = keyboard.Listener(on_press=lambda key: on_press(key, is_rec, should_stop))
    listener.start()

    try:
        # Main loop that can be interrupted with Ctrl+C
        while not should_stop.value:
            time.sleep(0.1)
    except KeyboardInterrupt:
        should_stop.value = True
        listener.stop()

    # Wait for the processes to finish
    print("Waiting for processes to finish...")
    read_process.join(timeout=1)
    record_process.join(timeout=1)

    # Print the final message
    print("Data collection stopped.")


if __name__ == "__main__":
    main()
