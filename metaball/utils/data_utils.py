#!/usr/bin/env python

"""
Utility functions for handling data.
"""

import os
import numpy as np
import cv2


def save_data(data: list[tuple], data_dir: str) -> None:
    """
    Save the data to files.

    Args:
        data_dir (str): The directory to save the data to.
        data (list): The data to save.
    """
    # Create a directory to save the data
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, "images"), exist_ok=True)
    print(f"Saving data to {data_dir}...")

    pose_list = []
    force_list = []
    # Save the data to files
    for i, d in enumerate(data):
        # Unpack the data
        pose, force, img = d

        # Save the image
        img_path = os.path.join(data_dir, "images", f"{i}.jpg")
        cv2.imwrite(img_path, img)

        # Add the pose and force data to the lists
        pose_list.append(pose)
        force_list.append(force)

    # Save the pose and force data to files
    pose_list = np.array(pose_list)
    force_list = np.array(force_list)
    np.savetxt(os.path.join(data_dir, "pose.csv"), pose_list, fmt="%.6f", delimiter=",")
    np.savetxt(os.path.join(data_dir, "force.csv"), force_list, fmt="%.6f", delimiter=",")

    # Print the number of frames saved
    print(f"Saved {len(data)} frames to {data_dir}.")


def force_sensor2global(force: np.ndarray, s2g_rmat: np.ndarray, s2g_tvec: np.ndarray) -> np.ndarray:
    """
    Convert the force/torque sensor data from the sensor frame to the global frame.

    Args:
        force (numpy.ndarray): The force/torque data from the sensor.
        s2g_rmat (numpy.ndarray): The rotation matrix from the sensor frame to the global frame.
        s2g_tvec (numpy.ndarray): The translation vector from the sensor frame to the global frame.

    Returns:
        np.ndarray: The converted force/torque data in the global frame.
    """

    global_force = np.zeros(6)
    # Convert the force to the global frame
    global_force[:3] = np.dot(s2g_rmat, force[:3])
    # Convert the torque to the global frame
    global_force[3:] = np.dot(s2g_rmat, force[3:]) + np.cross(s2g_tvec, global_force[:3])

    # Return the global force/torque data
    return global_force
