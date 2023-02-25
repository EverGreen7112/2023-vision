import math
import socket
import struct
import copy
import gbvision as gbv
import cv2 
import numpy as np
import april_tags
from pupil_apriltags import Detector
import send_game_pieces

# this code goes on the actual limelight's costume pipeline code section

at_detector = Detector(families="tag16h5", quad_sigma=0.8, decode_sharpening=0.4)
tags_pipe = gbv.ColorThreshold([[0, 255], [0, 255], [55, 255]], 'HSV') + gbv.Erode(1, 4) + gbv.Dilate(1, 4) 
robot_location_port = 5800
reflector_port = 5802
last_robot_location = [0, 0, 0]

def runPipeline(image, llrobot):
    global at_detector
    global tags_pipe
    global last_robot_location
    global robot_location_port
    global reflector_port
    
    
    debug_image = copy.deepcopy(image) # copy of original image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
    tags = at_detector.detect(
        tags_pipe(debug_image),
        estimate_tag_pose=False,
        camera_params=None,
        tag_size=None,
    )
    
    tags_points = [] # xyz of each corners of the tag in real life
    robot_locations = [] # all aproximations of robot locations
    for tag in tags:
        corners = tag.corners
        tag_xyz = april_tags.calc_tag_points_location(corners, april_tags.TAGS_CORNERS_HEIGHTS,
                                                                april_tags.LIMELIGHT_FOCAL_LENGTH_X, april_tags.LIMELIGHT_FOCAL_LENGTH_Y,
                                                                april_tags.FRAME_WIDTH, april_tags.FRAME_HEIGHT)
        try:
            robot_locations.append(april_tags.get_robot_field_location_by_tag(tag_xyz, april_tags.ID_FIELD_LOCATIONS[tag.id], april_tags.ID_FIELD_LOCATIONS_OFFSETS))
            tags_points.append(tag_xyz)
        except:
            pass
    reflector, cones, cubes, image = get_reflector_cones_cubes(debug_image)
    frame = april_tags.draw_tag(image, tags)
    if robot_locations == []:
        robot_location = april_tags.vectors_average(robot_locations) # average aproximation of robot location
    elif (reflector is not None):
        robot_location = (np.array(robot_location) + np.array(reflector) - np.array(last_reflector)).tolist()
    else:
        robot_location = last_robot_location 
    game_pieces_bytes = send_game_pieces.pack_game_pieces(cones, cubes)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(struct.pack('fff', robot_location[0],
                                        robot_location[1],
                                        robot_location[2]),
                        ("255.255.255.255", robot_location_port))
            sock.sendto(struct.pack('fff', reflector[0],
                                    reflector[1],
                                    reflector[2]), 
                        ("255.255.255.255", reflector_port))
            sock.sendto(game_pieces_bytes, 
                        ("255.255.255.255", send_game_pieces.port))
    except:
        pass
    last_robot_location = robot_location
    
    
    return [], frame, robot_location



reflectors_thr = gbv.ColorThreshold([[84, 104], [103, 223], [126, 255]], 'HSV') + gbv.MedianBlur(3) + gbv.Dilate(5, 1
        )  + gbv.Erode(5, 1)
cones_thr = gbv.ColorThreshold([[12, 22], [207, 255], [47, 147]], 'HSV') + gbv.MedianBlur(3) + gbv.Dilate(12, 3
        )  + gbv.Erode(12, 3) + gbv.DistanceTransformThreshold(0.1)
cubes_thr = gbv.ColorThreshold([[115, 125], [114, 174], [0, 94]], 'HSV') + gbv.MedianBlur(3) + gbv.Dilate(12, 3
        )  + gbv.Erode(12, 3) + gbv.DistanceTransformThreshold(0.1)
cones_pipe = cones_thr + gbv.find_contours + gbv.FilterContours(
    100) + gbv.contours_to_rotated_rects_sorted + gbv.filter_inner_rotated_rects
cubes_pipe = cubes_thr + gbv.find_contours + gbv.FilterContours(
    100) + gbv.contours_to_rotated_rects_sorted + gbv.filter_inner_rotated_rects
reflectors_pipe = reflectors_thr + gbv.find_contours + gbv.FilterContours(
    100) + gbv.contours_to_rotated_rects_sorted + gbv.filter_inner_rotated_rects

REFLECTOR = gbv.GameObject(math.sqrt(0.02 * 2.54 * (15/3200) * 2.54))
CONES = gbv.GameObject(0.2449489742783178)
CUBES = gbv.GameObject(0.21)
cam = gbv.USBCamera(0, gbv.CameraData(777.3291449774972, 1.0402162342 , 0.86742863824, pitch_angle=math.radians(25), name="limelight"))
FOCAL_LENGTH = 777.3291449774972
last_reflector = []
def get_reflector_cones_cubes(image):
        '''
        returns ([reflectors x, reflectors y, reflectors z], [cones: [x, y, z], [cubes: [x, y, z]], frame)
        reflectors is a single vector of the one reflector we want to focus on
        cones is a list of all cones seen
        cubes is a list of all cubes seen
        frame is the frame with the targets marked
        '''
        global reflectors_pipe, cones_pipe, cubes_pipe, cam
        cam.width = 960
        cam.height = 720
        
        frame = copy.deepcopy(image)
        cones_cnts = cones_pipe(frame)
        cubes_cnts = cubes_pipe(frame)
        reflectors_cnts = reflectors_pipe(frame)
        
        try:
                reflectors = [REFLECTOR.location_by_params(cam, gbv.BaseRotatedRect.shape_root_area(ref),
                                                           gbv.BaseRotatedRect.shape_center(ref)) for ref in reflectors_cnts]
        except:
                reflectors = []
        try:
                cones = [REFLECTOR.location_by_params(cam, gbv.BaseRotatedRect.shape_root_area(cone),
                                                           gbv.BaseRotatedRect.shape_center(cone)) for cone in cones_cnts]
        except:
                cones = []
        try:
                cubes = [REFLECTOR.location_by_params(cam, gbv.BaseRotatedRect.shape_root_area(cube),
                                                           gbv.BaseRotatedRect.shape_center(cube)) for cube in cubes_cnts]
        except:
                cubes = []
        reflector = choose_reflector(reflectors)
        frame = gbv.draw_rotated_rects(frame, cones_cnts, (0, 150, 255), thickness=5)
        frame = gbv.draw_rotated_rects(frame, cubes_cnts, (255, 0, 30), thickness=5)
        frame = gbv.draw_rotated_rects(frame, reflectors_cnts, (0, 255, 0), thickness=5)
        
        return reflector, cones, cubes, frame

def choose_reflector(reflectors):
        '''
        chooses which reflector to lock on to from all of the reflectors locations in real life
        '''
        global last_reflector
        if len(reflectors) == 0:
                last_ref = copy.deepcopy(last_reflector)
                last_reflector = None
                return last_ref
        if last_reflector == []:
                last_reflector = reflectors[0]
                return reflectors[0]
        last_ref = np.array(last_reflector)
        closest_match = np.array(reflectors[0])
        try:
            for i in range(len(reflectors)):
                    ref = reflectors[i]
                    if np.linalg.norm((np.array(ref) - last_ref)) <  np.linalg.norm((closest_match - last_ref)):
                            closest_match = np.array(ref)
        except:
            pass
        return closest_match.tolist()
                        