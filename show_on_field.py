import math
from threading import Thread
import cv2
import gbvision as gbv
import copy

METER_TO_PIXELS = 462.48821794645846
UNIT = 100
SHAPE = [[ UNIT, UNIT],
         [ UNIT, -UNIT],
         [-UNIT, -UNIT],
         [-UNIT, UNIT]]


xyz = [0,0,0]
rotation = 0

def show_on_field():
    window = gbv.FeedWindow("feed")
    window.open()
    field = cv2.imread('field.png')
    half_height, half_width, idfk = field.shape
    half_height *= 0.5
    half_width *= 0.5
    while True:
        frame = copy.deepcopy(field)
        shape = [[v[0] * math.cos(rotation) - v[1] * math.sin(rotation) + xyz[0]*METER_TO_PIXELS + half_width,
                  v[0] * math.sin(rotation) + v[1] * math.cos(rotation) + xyz[2]*METER_TO_PIXELS + half_height] for v in SHAPE]
        for i in range(len(shape)):
            v1 = shape[i]
            v2 = shape[(i+1)%len(shape)]
            cv2.line(frame, (int(v1[0]), int(v1[1])), 
                     (int(v2[0]), int(v2[1])),  (0,255,0), 100)
        # cv2.circle(frame, (int(xyz[0] + half_width), int(xyz[2] + half_height)), 1000, (255,0,0), 1000)
        window.show_frame(frame)
    


thread = Thread(target=show_on_field)

