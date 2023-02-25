import math
import numpy as np
import cv2
import time

CAM_HEIGHT = 0.60# estimate 
TAG_HEIGHT_FROM_FLOOR = 0.384175
TAG_SIDE_LENGTH = 0.1524
TAGS_CORNERS_HEIGHTS = [TAG_HEIGHT_FROM_FLOOR + TAG_SIDE_LENGTH - CAM_HEIGHT, 
                TAG_HEIGHT_FROM_FLOOR - CAM_HEIGHT,
                TAG_HEIGHT_FROM_FLOOR - CAM_HEIGHT,
                TAG_HEIGHT_FROM_FLOOR + TAG_SIDE_LENGTH - CAM_HEIGHT]

LIMELIGHT_FOV_W =  59.6 
LIMELIGHT_FOV_H = 45.7 
# focal length x and focal length y can be written:
# focal_length_x = 2 * tan(fov_width/2)
# focal_length_y = 2 * tan(fov_height/2)
# focal length is expressed as the ratio between the sensor and the actual focal length
LIMELIGHT_FOCAL_LENGTH_X = 2 * math.tan(math.radians(LIMELIGHT_FOV_W)/2)
LIMELIGHT_FOCAL_LENGTH_Y = 2 * math.tan(math.radians(LIMELIGHT_FOV_H)/2)

FRAME_WIDTH = 640
FRAME_HEIGHT = 480


ID_FIELD_LOCATIONS_OFFSETS = [8.270494, 0, 3.978656]
ID_FIELD_LOCATIONS = {
1: [610.77 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[0],
     18.22 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[1],
     42.19  * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[2]],
2: [610.77 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[0],
     18.22 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[1],
     108.19 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[2]],
3: [610.77 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[0],
     18.22 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[1],
     174.19 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[2]],
4: [636.96 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[0],
     27.38 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[1],
     265.74 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[2]],
5: [14.25  * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[0],
     27.3  * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[1],
     265.74 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[2]],
6: [40.45  * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[0],
     18.2  * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[1],
     174.19 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[2]],
7: [40.45  * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[0],
     18.2  * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[1],
     108.19 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[2]],
8: [40.45  * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[0],
     18.22 * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[1],
     42.19  * 2.54 / 100 - ID_FIELD_LOCATIONS_OFFSETS[2]] 
}

# this code goes to the libraries on the limelight

# let T be the function from the real life coordinates to the frame
# T: 3D space ---> 2D frame |  T(x, y, z) = (width * (x/(focal_length_x*z) + 0.5), height * (y/(focal_length_y*z) + 0.5))
# (T(x, y, z) - (0.5*width, 0.5*height)) * (focal_length_x, focal_length_y) / (width, height) = (x/z, y/z) 
# 1/(y/z) = z/y ---> (z/y) * y = z ---> (x/z) * z = x ---> and so we found x and z
def project_point(x, y, z):
    return [FRAME_WIDTH * (x/(LIMELIGHT_FOCAL_LENGTH_X*z) + 0.5), FRAME_HEIGHT * (y/(LIMELIGHT_FOCAL_LENGTH_Y*z) + 0.5)]
# camera matrix
#  |(w/fx) 0 w/2 |
#  |0 (h/fy) h/2 |
#  |0    0    1  |
CAMERA_MATRIX = np.array([[[FRAME_WIDTH/LIMELIGHT_FOCAL_LENGTH_X, 0.0, FRAME_WIDTH/2]],
                   [[0.0, FRAME_HEIGHT/LIMELIGHT_FOCAL_LENGTH_Y, FRAME_HEIGHT/2]],
                   [[0.0, 0.0, 1.0]]])
AXIS_MATRIX = np.array([[0.2, 0, 0],
                        [0, 0.2, 0], 
                        [0, 0, 0.2]])
TAG_MATRIX = np.array([[TAG_SIDE_LENGTH/2, TAG_SIDE_LENGTH/2, -TAG_SIDE_LENGTH],
                        [TAG_SIDE_LENGTH/2, -TAG_SIDE_LENGTH/2,  -TAG_SIDE_LENGTH], 
                        [-TAG_SIDE_LENGTH/2, -TAG_SIDE_LENGTH/2,  -TAG_SIDE_LENGTH]])
def pose_esitmation(frame):

    '''
    frame - Frame from the video stream
    matrix_coefficients - Intrinsic matrix of the calibrated camera
    distortion_coefficients - Distortion coefficients associated with your camera
    return:-
    frame - The frame with the axis drawn on it
    '''
    matrix_coefficients = CAMERA_MATRIX 
    distortion_coefficients =  np.array([0.0, 0.0, 0.0, 0.0, 0.0]) 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.aruco_dict = cv2.aruco.DICT_APRILTAG_16h5
    parameters = cv2.aruco.DetectorParameters()


    
    detector = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco_dict), parameters)
    corners, ids, rejected_img_points = detector.detectMarkers(gray)
    
    # If markers are detected
    cv2.aruco.drawDetectedMarkers(frame, corners) 
    tags_locations = []
    tags_rotations = []
     
    if len(corners) > 0:
        for i in range(0, len(ids)):
            # Estimate pose of each marker and return the values rvec and tvec---(different from those of camera coefficients)
            rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i],
                                                                           TAG_SIDE_LENGTH, matrix_coefficients, distortion_coefficients)
            # Draw a square around the markers
            center = average_2d(corners[i][0])
            center = (int(center[0]), int(center[1]))
            
            tags_rotations.append((np.array(rvec[0][0]) * 180 / math.pi).tolist())
            draw_tag(frame, ids[i][0], center, corners[i][0])
            # print(np.array(rvec[0][0]) * 180 / math.pi)
            rot = cv2.Rodrigues(-np.array(rvec))[0]
            pos = rot @ tvec[0][0]
            # tags_locations.append(pos)
            tags_locations.append(get_robot_field_location_by_tag(pos, ids[i][0], [0, 0, 0]))
            # # rotated_mat = AXIS_MATRIX
            # rotated_mat = rot[0] @ AXIS_MATRIX
            # # mat = (rot[0] @ TAG_MATRIX).tolist()
            # mat = TAG_MATRIX.tolist()
            # mat.append((np.array(mat[1]) * -1).tolist())
            # mat[3][2] *= -1
            # tags_matrices.append(mat)
            # # rotated_mat = rotate(rvec[0][0][1], -rvec[0][0][2], rvec[0][0][0], AXIS_MATRIX)
            # colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]
            # for i in range(len(mat)):
            #     mat[i] = (np.array(mat[i]) + np.array(tvec[0][0])).tolist()
            #     mat[i] = project_point(mat[i][0], mat[i][1], mat[i][2])
            # draw_tag(frame, '', average_2d(mat), mat)
            # for i in range(len(rotated_mat)):
            #     rotated_mat[i] = (np.array(rotated_mat[i]) + np.array(tvec[0][0])).tolist()
            #     frame_xy = project_point(rotated_mat[i][0], rotated_mat[i][1], rotated_mat[i][2])
            #     frame_xy = (int(frame_xy[0]), int(frame_xy[1]))
            #     cv2.line(frame, frame_xy, center, colors[i], 5)

            # Draw Axis
            cv2.drawFrameAxes(frame,np.array([a[0] for a in matrix_coefficients.tolist()]), distortion_coefficients, rvec, tvec, 0.2, 3)  
            

    return frame, tags_locations, tags_rotations

def vectors_average_3d(vectors):
    sum = np.array([0.0, 0.0, 0.0])
    for v in vectors:
        sum += np.array(v)
    try:
        return (sum / len(vectors)).tolist()
    except:
        return [0.0, 0.0, 0.0]
def get_robot_field_location_by_tag(tag_location, id, offset):
    '''
    gets the robots location on the field by tag points and tag field location
    :param tag_location: the xyz location in real life of the tag
    :param tag_in_field: the xyz location of the tag on the field
    '''
    tag_in_field = ID_FIELD_LOCATIONS[id]
    xyz_t = np.array(tag_in_field) - np.array(offset)
    return (xyz_t - np.array([tag_location[len(tag_location) - 1 - i] for i in range(len(tag_location))])).tolist()

def draw_tag(image, tag_id, center, corners):
    # tag_family = tag.tag_family


    center = (int(center[0]), int(center[1]))
    corner_01 = (int(corners[0][0]), int(corners[0][1]))
    corner_02 = (int(corners[1][0]), int(corners[1][1]))
    corner_03 = (int(corners[2][0]), int(corners[2][1]))
    corner_04 = (int(corners[3][0]), int(corners[3][1]))
    # line1_center = (int(line1_center[0]), int(line1_center[1]))
    # line2_center = (int(line2_center[0]), int(line2_center[1]))
    cv2.circle(image, (center[0], center[1]), 5, (0, 0, 255), 2)
    # cv.circle(image, (line2_center[0], line2_center[1]), 5, (0, 255, 0), 2)
    # cv.circle(image, (line1_center[0], line1_center[1]), 5, (0, 0, 255), 2)
    cv2.putText(image, str(tag_id), (center[0] - 10, center[1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.line(image, (corner_01[0], corner_01[1]),
            (corner_02[0], corner_02[1]), (0, 0, 255), 2)
    cv2.line(image, (corner_02[0], corner_02[1]),
            (corner_03[0], corner_03[1]), (0, 0, 255), 2)
    cv2.line(image, (corner_03[0], corner_03[1]),
            (corner_04[0], corner_04[1]), (0, 255, 0), 2)
    cv2.line(image, (corner_04[0], corner_04[1]),
            (corner_01[0], corner_01[1]), (0, 255, 0), 2)
    return image

def average_2d(corners):
    sum_x = 0
    sum_y = 0
    for c in corners:
        sum_x += c[0]
        sum_y += c[1]
    return [sum_x/len(corners), sum_y/len(corners)]

def rotate(yaw, pitch, roll, matrix):
    """
    Applies a yaw-pitch-roll rotation to a 3x3 matrix using the Euler rotation matrix.
    
    :param yaw: the yaw angle in radians
    :param pitch: the pitch angle in radians
    :param roll: the roll angle in radians
    :param matrix: the 3x3 matrix to be rotated
    :return: the rotated 3x3 matrix
    """
    
    # Define the Euler rotation matrix
    R_yaw = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                      [np.sin(yaw), np.cos(yaw), 0],
                      [0, 0, 1]])
    
    R_pitch = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                        [0, 1, 0],
                        [-np.sin(pitch), 0, np.cos(pitch)]])
    
    R_roll = np.array([[1, 0, 0],
                       [0, np.cos(roll), -np.sin(roll)],
                       [0, np.sin(roll), np.cos(roll)]])
    
    # Combine the three rotations
    R = R_yaw @ R_pitch @ R_roll
    # R = R_pitch @ R_yaw @ R_roll
    
    # Apply the rotation to the matrix
    rotated_matrix = R @ matrix
    
    return rotated_matrix     

# def main():

#     # ap = argparse.ArgumentParser()
#     # ap.add_argument("-k", "--K_Matrix", required=True, help="Path to calibration matrix (numpy file)")
#     # ap.add_argument("-d", "--D_Coeff", required=True, help="Path to distortion coefficients (numpy file)")
#     # ap.add_argument("-t", "--type", type=str, default="DICT_ARUCO_ORIGINAL", help="Type of ArUCo tag to detect")
#     # args = vars(ap.parse_args())


#     # calibration_matrix_path = args["K_Matrix"]
#     # distortion_coefficients_path = args["D_Coeff"]
    
#     # k = np.load(calibration_matrix_path)


#     video = cv2.VideoCapture(1)
#     time.sleep(2.0)

#     while True:
#         ret, frame = video.read()

#         if not ret:
#             break
        
#         output, p, r = pose_esitmation(frame)
#         print(p)

#         cv2.imshow('Estimated Pose', output)

#         key = cv2.waitKey(1) & 0xFF
#         if key == ord('q'):
#             break

#     video.release()
#     cv2.destroyAllWindows()
    
# if __name__ == '__main__':
#     main()
    