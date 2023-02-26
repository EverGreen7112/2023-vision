import copy
import math
import socket
import struct
import cv2 as cv
import numpy as np
import april_tags2 as ap2
import gbvision as gbv
import send_game_pieces
robot_location_port = 5800
reflector_port = 5802
robot_location = [0, 0, 0]
last_robot_location = [0, 0, 0]
def runPipeline(image, llrobot):
    global robot_location_port, robot_location, last_robot_location, last_reflector
    frame = copy.deepcopy(image)
    output, positions, rotations = ap2.pose_esitmation(frame)

    reflector, cones, cubes, frame = get_reflector_cones_cubes(frame)
    if len(positions) > 0:
        robot_location = ap2.vectors_average_3d(positions)
    elif (reflector != [] and reflector is not None and last_reflector != [] and last_reflector is not None):
        robot_location = (np.array(last_robot_location) + np.array(reflector) - np.array(last_reflector)).tolist()
    else:
        robot_location = last_robot_location 
    game_pieces_bytes = send_game_pieces.pack_game_pieces(cones, cubes)
    print("cubes: "+str(cubes))
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            sock.sendto(struct.pack('fff', robot_location[0],
                                        robot_location[1],
                                        robot_location[2]),
                        ("255.255.255.255", robot_location_port))
        except:
            pass
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            sock.sendto(struct.pack('fff', reflector[0],
                                    reflector[1],
                                    reflector[2]), 
                        ("255.255.255.255", reflector_port))
        except:
            pass
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            sock.sendto(game_pieces_bytes, 
                        ("255.255.255.255", send_game_pieces.port))
        except:
            pass
    last_robot_location = copy.deepcopy(robot_location)
    return [], frame, robot_location


class Tag:
    def __init__(self, corners, id) -> None:
           self.corners = corners
           self.tag_id = id
           self.center = [(corners[0][0] + corners[1][0] + corners[2][0] + corners[3][0])/4, 
                          (corners[0][1] + corners[1][1] + corners[2][1] + corners[3][1])/4]


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
cam = gbv.USBCamera(0, gbv.CameraData(777.3291449774972, 1.0402162342 , 0.86742863824, name="limelight"))
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
        cam.width = ap2.FRAME_WIDTH
        cam.height = ap2.FRAME_HEIGHT
        
        # frame = copy.deepcopy(image)
        frame = image
        cones_cnts = cones_pipe(frame)
        cubes_cnts = cubes_pipe(frame)
        reflectors_cnts = reflectors_pipe(frame)
        
        try:
                reflectors = [REFLECTOR.location_by_params(cam, gbv.BaseRotatedRect.shape_root_area(ref),
                                                           gbv.BaseRotatedRect.shape_center(ref)).tolist() for ref in reflectors_cnts]
        except:
                reflectors = []
        try:
                cones = [CONES.location_by_params(cam, gbv.BaseRotatedRect.shape_root_area(cone),
                                                           gbv.BaseRotatedRect.shape_center(cone)).tolist() for cone in cones_cnts]
        except:
                cones = []
        try:
                cubes = [CUBES.location_by_params(cam, gbv.BaseRotatedRect.shape_root_area(cube),
                                                           gbv.BaseRotatedRect.shape_center(cube)).tolist() for cube in cubes_cnts]
        except:
                cubes = []
        reflector = choose_reflector(reflectors)
        frame = gbv.draw_rotated_rects(frame, cones_cnts, (0, 150, 255), thickness=5)
        frame = gbv.draw_rotated_rects(frame, cubes_cnts, (255, 0, 30), thickness=5)
        frame = gbv.draw_rotated_rects(frame, reflectors_cnts, (0, 255, 0), thickness=5)
        cones = [cone for cone in cones if not (math.isnan(cone[0]) or math.isnan(cone[1]) or math.isnan(cone[2]))]
        cubes = [cube for cube in cubes if not (math.isnan(cube[0]) or math.isnan(cube[1]) or math.isnan(cube[2]))]
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

# temp
def main():
        cam = gbv.USBCamera(1)
        cam.set_exposure(-7)
        ok, frame = cam.read()
        win = gbv.FeedWindow("window")
        while True:
                a, frame, b = runPipeline(frame, [])
                win.show_frame(frame)
                ok, frame = cam.read()

if __name__ == '__main__':
        main()