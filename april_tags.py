import math
import numpy as np
import cv2 as cv


# this code goes to the libraries on the limelight

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


ID_FIELD_LOCATIONS_OFFSETS = [8.270494, 0, 4.576826]
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
# let T be the function from the real life coordinates to the frame
# T: 3D space ---> 2D frame |  T(x, y, z) = (width * (x/(focal_length_x*z) + 0.5), height * (y/(focal_length_y*z) + 0.5))
# (T(x, y, z) - (0.5*width, 0.5*height)) * (focal_length_x, focal_length_y) / (width, height) = (x/z, y/z) 
# 1/(y/z) = z/y ---> (z/y) * y = z ---> (x/z) * z = x ---> and so we found x and z
def calc_point_by_height(x_frame, y_frame, y_irl, focal_length_x, focal_length_y, frame_width, frame_height): 
    '''
    calculates point location in 3d space by is height in 3d space and its coordinates in frame
    
    focal length x and focal length y are expressed:
    focal_length_x = 2 * tan(fov_width/2)
    focal_length_y = 2 * tan(fov_height/2)
    
    the geometric meaning is the size of the sensor divided by the physical distance between the pinhole and sensor
    '''
    print(x_frame)
    x_y_by_z = (np.array([x_frame, y_frame]) - np.array([0.5 * frame_width, 0.5 * frame_height])) * \
        np.array([focal_length_x, focal_length_y]) / np.array([frame_width, frame_height])
    print(x_y_by_z)
    z = (1/(x_y_by_z[1])) * y_irl
    x = x_y_by_z[0] * z
    return (x, y_irl, z)

def calc_tag_location(corners, id):
    x = 0
    y = 0
    for corner in corners:
        x += corner[0]
        y += corner[1]
    x /= len(corners)
    y /= len(corners)
    return calc_point_by_height(x, y, ID_FIELD_LOCATIONS[id][1] - CAM_HEIGHT, LIMELIGHT_FOCAL_LENGTH_X, LIMELIGHT_FOCAL_LENGTH_Y, FRAME_WIDTH, FRAME_HEIGHT)


def get_robot_location(corners, id):
    tag_xyz = np.array(calc_tag_location(corners, id))
    return (np.array(ID_FIELD_LOCATIONS[id]) - tag_xyz).tolist()
    

def calc_tag_points_location(corners, corners_heights, focal_length_x, focal_length_y, frame_width, frame_height):
    '''
    takes a matrix of all points (array of four) in the 2d frame and their height irl and returns a matrix of all points in 3d space
    
    :param corners: corners location in frame
    :param corners_heights: corners heights irl
    focal length x and focal length y are expressed:
    focal_length_x = 2 * tan(fov_width/2)
    focal_length_y = 2 * tan(fov_height/2)
    
    the geometric meaning is the size of the sensor divided by the physical distance between the pinhole and sensor
    
    '''
    points = []
    for i in range(len(corners)):
        points.append(calc_point_by_height(corners[i][0], corners[i][1], corners_heights[i], focal_length_x, focal_length_y,
                                       frame_width, frame_height))
    return points


def get_robot_field_location_by_tag(tag_corners_irl, tag_in_field, offset):
    '''
    gets the robots location on the field by tag points and tag field location
    :param tag_corners_irl: the xyz location in real life of each corner of the tag
    :param tag_in_field: the xyz location of the tag on the field
    '''
    xyz_t = np.array(tag_in_field) - np.array(offset)
    return (xyz_t - np.array( vectors_average(tag_corners_irl))).tolist()

def vectors_average(vectors):
    sum = np.array([0.0, 0.0, 0.0])
    for v in vectors:
        sum += np.array(v)
    try:
        return (sum / len(vectors)).tolist()
    except:
        return [0.0, 0.0, 0.0]

def draw_tag(image, tag):
    # tag_family = tag.tag_family
    tag_id = tag.tag_id
    center = tag.center
    corners = tag.corners

    center = (int(center[0]), int(center[1]))
    corner_01 = (int(corners[0][0]), int(corners[0][1]))
    corner_02 = (int(corners[1][0]), int(corners[1][1]))
    corner_03 = (int(corners[2][0]), int(corners[2][1]))
    corner_04 = (int(corners[3][0]), int(corners[3][1]))
    # line1_center = (int(line1_center[0]), int(line1_center[1]))
    # line2_center = (int(line2_center[0]), int(line2_center[1]))
    cv.circle(image, (center[0], center[1]), 5, (0, 0, 255), 2)
    # cv.circle(image, (line2_center[0], line2_center[1]), 5, (0, 255, 0), 2)
    # cv.circle(image, (line1_center[0], line1_center[1]), 5, (0, 0, 255), 2)
    cv.putText(image, str(tag_id), (center[0] - 10, center[1] - 10),
        cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv.LINE_AA)
    cv.line(image, (corner_01[0], corner_01[1]),
            (corner_02[0], corner_02[1]), (0, 0, 255), 2)
    cv.line(image, (corner_02[0], corner_02[1]),
            (corner_03[0], corner_03[1]), (0, 0, 255), 2)
    cv.line(image, (corner_03[0], corner_03[1]),
            (corner_04[0], corner_04[1]), (0, 255, 0), 2)
    cv.line(image, (corner_04[0], corner_04[1]),
            (corner_01[0], corner_01[1]), (0, 255, 0), 2)
    return image
