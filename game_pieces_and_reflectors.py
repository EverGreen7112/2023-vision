from copy import copy
import math
import gbvision as gbv
import cv2 
import numpy as np



# vals = 94, 213, 216
# range = 10, 110, 90

reflector_port = 5802

reflectors_thr = gbv.ColorThreshold([[84, 104], [103, 223], [126, 255]])
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
def get_reflectors_cones_cubes(image):
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
        for i in range(len(reflectors)):
                ref = reflectors[i]
                if np.linalg.norm((np.array(ref) - last_ref)) <  np.linalg.norm((closest_match - last_ref)):
                        closest_match = np.array(ref)
        return closest_match.tolist()
                        