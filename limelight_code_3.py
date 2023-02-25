import copy
import socket
import struct
import cv2 as cv
import april_tags2 as ap2
robot_location_port = 5800
robot_location = [0, 0, 0]
def runPipeline(image, llrobot):
    global robot_location_port, robot_location
    frame = copy.deepcopy(image)
    output, positions, rotations = ap2.pose_esitmation(frame)
    if len(positions) > 0:
        robot_location = ap2.vectors_average_3d(positions)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            sock.sendto(struct.pack('fff', robot_location[0],
                                        robot_location[1],
                                        robot_location[2]),
                        ("255.255.255.255", robot_location_port))
        except:
            pass
    return  [], frame, []
