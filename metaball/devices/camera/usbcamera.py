#!/usr/bin/env python

import argparse
import time
import cv2
import yaml
import numpy as np
from scipy.spatial.transform import Rotation as spR


# Camera class
class UsbCamera:
    def __init__(
        self,
        id: int = 0,
        mark_size: float = 0.012,
        field: str = "land",
        resolution: str = "1080p",
        filter_on: bool = False,
        filter_frame: int = 5,
    ) -> None:
        """Camera driver class.

        This class is used to read the pose and image from the camera.
        The image is read from the USB camera.
        The pose is calculated by the ArUco marker.

        Args:
            mark_size: float, the size of the marker
            field: str, the field of the camera
            resolution: str, the resolution of the camera
            filter_on: bool, the filter flag
            filter_frame: int, the filter frame

        Returns:
            None
        """

        # Set the camera parameters
        with open(f"./modules/cam/config/camera_{id}.yaml", "r") as f:
            camera_params = yaml.load(f.read(), Loader=yaml.Loader)
            self.width = int(camera_params[resolution]["width"])
            self.height = int(camera_params[resolution]["height"])
            self.fps = int(camera_params[resolution]["fps"])
            self.mtx = np.array(camera_params[resolution]["mtx"][field])
            self.dist = np.array(camera_params[resolution]["dist"][field])

        # Set the camera parameters
        self.camera = cv2.VideoCapture(id)
        self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.camera.set(
            cv2.CAP_PROP_AUTO_EXPOSURE, 0.75
        )  # fixed exposure 0.25, automatic 0.75
        # self.camera.set(cv2.CAP_PROP_FPS, self.fps)

        # Set the detector parameters
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        aruco_params = cv2.aruco.DetectorParameters()
        with open("./modules/cam/config/detector.yaml", "r") as f:
            detector_params = yaml.load(f.read(), Loader=yaml.Loader)
            for key in detector_params:
                aruco_params.__setattr__(key, detector_params[key])
        self.detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

        # Set the marker size
        self.mark_size = mark_size

        # Set the initial pose
        self.init_pose = np.zeros(6)

        # Set the pose
        self.pose = np.zeros(6)

        # Set the filter parameters
        self.filter_on = filter_on
        self.filter_frame = filter_frame
        self.last_pose = np.zeros(6)
        self.pose_list = []
        self.img = np.zeros((self.height, self.width, 3))
        self.first_frame = True

        # Init pose
        for i in range(5):
            self.read_img()
            time.sleep(0.5)
        self.init_pose = self.cal_init_pose()
        self.init_tvec = self.init_pose[:3]
        self.init_rvec = self.init_pose[3:]
        self.init_rmat = spR.as_matrix(spR.from_rotvec(self.init_rvec))
        self.init_mat = self.pose_mat(self.init_pose)

    def cal_init_pose(self) -> np.array:
        """Calculate the initial pose.

        After 10 frames, the function will calculate the mean of the pose and return it.

        Args:
            None

        Returns:
            pose: np.array([x, y, z, rx, ry, rz])
        """

        # Create lists to store the tvec and rvec
        tvec_list = []
        rvec_list = []

        # Get the pose for 100 frames
        for i in range(10):
            pose, _ = self.read_img_pose()
            tvec_list.append(pose[:3])
            rvec_list.append(pose[3:])

        # Calculate the mean of the pose
        tvec_list = np.array(tvec_list)
        rvec_list = np.array(rvec_list)
        tvec = np.mean(tvec_list, axis=0)
        rvec = spR.from_rotvec(rvec_list).mean().as_rotvec()
        pose = np.hstack((tvec, rvec))

        # Return the pose
        return pose

    def read_img(self) -> np.array:
        """Read the image from the camera.

        Using the OpenCV, the function will read the image from the camera.
        If the image is not read, the function will raise an error.

        Args:
            None

        Returns:
            img: np.array([height, width, 3])

        Raises:
            ValueError: Cannot read the image from the camera.
        """

        # Read the image from the camera
        ret, img = self.camera.read()
        # Check if the image is read
        if not ret:
            ValueError("Cannot read the image from the camera.")
        # Return the image
        return img

    def release(self) -> None:
        """Release the camera.

        The function will close the window.

        Args:
            None

        Returns:
            None
        """

        # Release the camera
        self.camera.release()
        # Close the window
        cv2.destroyAllWindows()

    def img2pose(self, img):
        """Get the pose and image from the camera.

        The function is to get the pose and image from the camera.
        First, the image is converted to the gray image and filtered by the kernel.
        Then, the ArUco markers are detected and the pose is estimated.
        Finally, the pose is filtered and the markers are drawn on the image.

        Args:
            img: np.array([height, width, 3])

        Returns:
            pose: np.array([x, y, z, rx, ry, rz])
            img: np.array([height, width, 3])
        """

        # Convert the image to gray
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Apply the filter to the image
        kernel = np.ones((5, 5), np.float32) / 25
        gray = cv2.filter2D(gray, -1, kernel)
        gray = cv2.medianBlur(gray, 5)

        # Detect the markers
        corners, ids, rejected = self.detector.detectMarkers(gray)
        # Check if the markers are detected
        if ids is None:
            return np.zeros(6), img

        # Estimate the pose
        rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
            corners[0], self.mark_size, self.mtx, self.dist
        )
        pose = np.hstack((tvec[0] * 1000, rvec[0])).flatten()

        # Filter the pose
        if self.filter_on:
            pose = self.pose_filter(pose)

        # Draw the markers
        color_image_result = cv2.aruco.drawDetectedMarkers(img, corners, ids)
        color_image_result = cv2.drawFrameAxes(
            img, self.mtx, self.dist, rvec[0], tvec[0], self.mark_size
        )
        # Return the pose and image
        return pose, color_image_result

    def read_img_pose(self):
        """Read the pose and image from the camera.

        The function is to read the pose and image from the camera.
        The pose and image are got from the img2pose function.

        Returns:
            pose: np.array([x, y, z, rx, ry, rz])
            img: np.array([height, width, 3])
        """

        # Read the image from the camera
        img = self.read_img()

        # Get the pose and image from the camera
        pose, img = self.img2pose(img)
        # Check if the first frame
        if self.first_frame:
            self.first_frame = False
            self.last_pose = pose
        # Check if the pose is valid
        if np.linalg.norm(pose[:3] - self.last_pose[:3]) > 20:
            self.pose = self.last_pose
        else:
            self.pose = pose
        self.last_pose = self.pose
        self.img = img
        # Return the pose and image
        return self.pose, self.img

    def pose2ref(self, pose) -> np.array:
        """Convert the pose to the reference pose.

        The function is to calculate the reference pose by the initial pose.
        The tvec is the difference between the current tvec and the initial tvec.
        The rvec is the matrix multiplication of the inverse of the initial rvec and the current rvec.

        Args:
            pose: np.array([x, y, z, rx, ry, rz])

        Returns:
            refPose: np.array([x, y, z, rx, ry, rz])
        """

        # Convert rvec
        rvec = pose[3:]
        rmat = spR.as_matrix(spR.from_rotvec(rvec))
        rmat = np.linalg.inv(self.init_rmat) @ rmat
        rvec = spR.from_matrix(rmat).as_rotvec()

        # Convert tvec
        tvec = np.linalg.inv(self.init_rmat) @ (pose[:3] - self.init_tvec)

        # Create the reference pose
        ref_pose = np.hstack((tvec, rvec))

        # Return the reference pose
        return ref_pose

    def pose_marker2cam(self, pose) -> np.array:
        """Convert the pose to the camera frame.

        The function is to convert the pose to the camera frame.
        The translation matrix is:
        [[1, 0, 0, x],
         [0,-1, 0, y],
         [0, 0,-1, z],
         [0, 0, 0, 1]].
        The pose is represented by [x, y, z, rx, ry, rz].

        Args:
            pose: np.array([x, y, z, rx, ry, rz])

        Returns:
            pose_cam: np.array([x, y, z, rx, ry, rz])
        """

        # Convert the pose to the camera frame
        trans_rmat = np.array([[0, 1, 0], [1, 0, 0], [0, 0, -1]])
        rvec = trans_rmat @ pose[3:]
        tvec = trans_rmat @ pose[:3]

        pose_cam = np.hstack((tvec, rvec))

        return pose_cam

    def pose_euler(self, pose) -> np.array:
        """Convert the pose to the euler angles.

        The function is to convert the pose to the euler angles.
        The unit of the euler angles is radian.

        Args:
            pose: np.array([x, y, z, rx, ry, rz])

        Returns:
            pose_euler: np.array([x, y, z, rx, ry, rz])
        """

        # Convert rvec to euler angles
        rvec = pose[3:]
        rr = spR.from_rotvec(rvec)
        rpy = rr.as_euler("xyz", degrees=False)

        # Create the euler pose
        pose_euler = np.hstack((pose[:3], rpy))

        # Return the euler pose
        return pose_euler

    def pose_quat(self, pose) -> np.array:
        """Convert the pose to the quaternion.

        The function is to convert the pose to the quaternion.
        The quaternion is represented by [x, y, z, qx, qy, qz, qw].

        Args:
            pose: np.array([x, y, z, rx, ry, rz])

        Returns:
            pose_quat: np.array([x, y, z, qx, qy, qz, qw])
        """

        # Convert rvec to quaternion
        rvec = pose[3:]
        rr = spR.from_rotvec(rvec)
        quat = rr.as_quat()

        # Create the quaternion pose
        pose_quat = np.hstack((pose[:3], quat))

        # Return the quaternion pose
        return pose_quat

    def pose_mat(self, pose) -> np.array:
        """Convert the pose to the matrix.

        The function is to convert the pose to the matrix.
        The matrix is represented by
        [[r11, r12, r13, x],
         [r21, r22, r23, y],
         [r31, r32, r33, z],
         [  0,   0,   0, 1]].

        Args:
            pose: np.array([x, y, z, rx, ry, rz])

        Returns:
            pose_matrix: np.array([4, 4])
        """

        # Convert rvec to matrix
        rvec = pose[3:]
        rr = spR.from_rotvec(rvec)

        # Create the matrix pose
        pose_matrix = np.eye(4)
        pose_matrix[:3, :3] = rr.as_matrix()
        pose_matrix[:3, 3] = pose[:3]

        # Return the matrix pose
        return pose_matrix

    def pose_filter(self, pose, frame=5) -> np.array:
        """Filter the pose.

        The function is to filter the pose by the mean of the pose list.
        If the pose list is less than the frame, the pose will be appended to the pose list directly.
        Otherwise, the first pose will be popped and the pose will be appended to the pose list.

        Args:
            pose: np.array([x, y, z, rx, ry, rz])
            frame: int, the frame number

        Returns:
            filtered_pose: np.array([x, y, z, rx, ry, rz])
        """

        # Check if the pose list is less than the frame
        if len(self.pose_list) < frame:
            # Append the pose to the pose list
            self.pose_list.append(pose)
        else:
            # Pop the first pose and append the pose to the pose list
            self.pose_list.pop(0)
            self.pose_list.append(pose)

        # Calculate the mean of the pose list
        tvec_list = np.array([pose[:3] for pose in self.pose_list])
        rvec_list = np.array([pose[3:] for pose in self.pose_list])
        tvec = np.mean(tvec_list, axis=0)
        rvec = spR.from_rotvec(rvec_list).mean().as_rotvec()

        # Create the filtered pose
        filtered_pose = np.hstack((tvec, rvec))

        # Copy the filtered pose to the last pose
        self.pose_list[-1] = filtered_pose

        # Return the filtered pose
        return filtered_pose

    def bgr2rgb(self, img) -> np.array:
        """Convert the BGR image to the RGB image.

        The function is to convert the BGR image to the RGB image using the OpenCV.
        BGR is the default color space of the OpenCV.
        RGB is the default color space of the Matplotlib and other libraries.
        It is necessary to convert the BGR image to the RGB image before using other libraries.

        Args:
            img: np.array([height, width, 3])

        Returns:
            img: np.array([height, width, 3])
        """

        # Convert the BGR image to the RGB image
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


if __name__ == "__main__":
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mark_size",
        default=0.012,
        type=float,
        help="Size of the marker (default: 0.012).",
    )
    parser.add_argument(
        "--field",
        default="land",
        type=str,
        help="Application field, including land, and water (default: land).",
    )
    parser.add_argument(
        "--resolution", default="1080p", type=str, help="Resolution (default: 1080p)."
    )
    parser.add_argument(
        "--filter", action="store_true", help="Filter to apply to the image."
    )
    parser.add_argument(
        "--show-img",
        action="store_true",
        help="Show the images",
    )
    args = parser.parse_args()

    # Create a camera
    camera = UsbCamera(
        mark_size=args.mark_size,
        field=args.field,
        resolution=args.resolution,
        filter_on=args.filter,
        filter_frame=5,
    )

    show_img = args.show_img

    # Start the loop
    while True:
        # Get the pose and image from the camera
        pose, frame = camera.read_img_pose()
        # Convert the pose to the reference pose
        pose = camera.pose2ref(pose)
        # Convert the pose to the euler angles
        pose = camera.pose_euler(pose)

        # Print the pose
        print(
            "Dx: %3.3f, Dy: %3.3f, Dz: %3.3f, Rx: %3.3f, Ry: %3.3f, Rz: %3.3f"
            % (pose[0], pose[1], pose[2], pose[3], pose[4], pose[5]),
            end="\r",
        )

        if show_img:
            # Show the image
            cv2.imshow("Camera", frame)

            # Break the loop
            if cv2.waitKey(10) == 27:
                break

    # Release the camera
    print("\n")
    camera.release()
