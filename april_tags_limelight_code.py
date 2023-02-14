import math
import socket
import struct
import copy
import gbvision as gbv
import cv2 
import numpy as np
import april_tags
from pupil_apriltags import Detector

# this code goes on the actual limelight's costume pipeline code section

at_detector = Detector(families="tag16h5", quad_sigma=0.8, decode_sharpening=0.4)
tags_pipe = gbv.ColorThreshold([[0, 255], [0, 255], [55, 255]], 'HSV') + gbv.Erode(1, 4) + gbv.Dilate(1, 4) 
robot_location_port = 5800

def runPipeline(image, llrobot):
    global at_detector
    global tags_pipe
    global robot_location_port
    
    
    debug_image = copy.deepcopy(image) # copy of original image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
    tags = at_detector.detect(
        tags_pipe(debug_image),
        estimate_tag_pose=False,
        camera_params=None,
        tag_size=None,
    )
    frame = april_tags.draw_tags(image, tags)
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
        
    robot_location = april_tags.vectors_average(robot_locations) # average aproximation of robot location
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(struct.pack('fff', robot_location[0],
                                       robot_location[1],
                                       robot_location[2]),
                    ("255.255.255.255", robot_location_port))
    
    
    return [], frame, robot_location