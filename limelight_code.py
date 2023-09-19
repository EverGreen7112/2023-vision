import socket
import struct
import copy
import gbvision as gbv
import cv2 
import april_tags_utils as ap
from pupil_apriltags import Detector
import settings

# this code is only for the april tags

# at_detector = Detector(families="tag16h5", quad_sigma=0.8, decode_sharpening=0.4)
port = 5800
last_robot_location = [0, 0, 0]

def runPipeline(image, llrobot):
    # global at_detector
    global tags_pipe
    global last_robot_location
    global port
    
    
    debug_image = copy.deepcopy(image) # copy of original image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
    all_c_3d, ids = ap.process_frame(frame, settings.TAG_SIDE_LENGTH, settings.LIMELIGHT_FOCAL_LENGTH)
    try:
        frame = ap.draw_tags(frame, all_c_3d, settings.LIMELIGHT_FOCAL_LENGTH, settings.TAG_SIDE_LENGTH)
    except: 
        pass
    
    
    
    if robot_location == []:
        robot_location = april_tags.vectors_average(robot_locations) # average aproximation of robot location
    else:
        # TODO: add code for using reflectors instead
        # temp
        robot_location = last_robot_location 
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(struct.pack('fff', robot_location[0],
                                       robot_location[1],
                                       robot_location[2]),
                    ("255.255.255.255", port))
    last_robot_location = robot_location
    
    
    return [], frame, robot_location