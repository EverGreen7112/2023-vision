import struct
import socket

port = 5801 # cant be this in actual competition


def pack_game_pieces(cones, cubes):
    cones_ammount = len(cones)
    cubes_ammount = len(cubes)
    
    worked_array = tuple(cones) + tuple(cubes)
    bytes_pack = struct.pack('ii', cones_ammount, cubes_ammount)
    for v in worked_array:
        bytes_pack += struct.pack('f', v[0])
        bytes_pack += struct.pack('f', v[1])
        bytes_pack += struct.pack('f', v[2])
    
    return bytes_pack