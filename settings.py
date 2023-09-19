import math
TAG_FIELD_LOCATIONS_OFFSETS = [8.270494, 0, 4.576826] # offset to add to each tag, used to convert to the field coordinates system as written in the readme
TAGS_CENTERS_LOCATIONS = {
1: [-(610.77 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[0]),
    ( 18.22 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[1]),
    -( 42.19  * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[2])],
2: [-(610.77 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[0]),
    ( 18.22 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[1]),
    -( 108.19 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[2])],
3: [-(610.77 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[0]),
    ( 18.22 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[1]),
    -( 174.19 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[2])],
4: [-(636.96 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[0]),
    ( 27.38 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[1]),
    -( 265.74 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[2])],
5: [-(14.25  * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[0]),
    ( 27.3  * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[1]),
    -( 265.74 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[2])],
6: [-(40.45  * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[0]),
    ( 18.2  * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[1]),
    -( 174.19 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[2])],
7: [-(40.45  * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[0]),
    ( 18.2  * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[1]),
    -( 108.19 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[2])],
8: [-(40.45  * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[0]),
    ( 18.22 * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[1]),
    -( 42.19  * 2.54 / 100 - TAG_FIELD_LOCATIONS_OFFSETS[2])]  
} # this is the dict that tells you the location of each tags center in field coords
TAGS_ROTATIONS = {1: 0, 2: 0, 3: 0, 4: 0, 5: 180, 6: 180, 7: 180, 8: 180 } # tags rotation around the y axis
TAG_SIDE_LENGTH = 0.153 # the length of a side of the tag
TAG_SHAPE = [
    [0, -TAG_SIDE_LENGTH/2, TAG_SIDE_LENGTH/2 ],
    [0, -TAG_SIDE_LENGTH/2, -TAG_SIDE_LENGTH/2 ],
    [0, TAG_SIDE_LENGTH/2, -TAG_SIDE_LENGTH/2 ],
    [0, TAG_SIDE_LENGTH/2, TAG_SIDE_LENGTH/2 ]
] # the coordinates of each corener of a tag whose center sits on (0,0,0) and whose rotation is 0

def rotate_around_y(vec: list, angle_degrees: float):
    ret_vec = []
    theta_r = math.radians(angle_degrees)
    ret_vec.append(vec[0] * math.cos(theta_r) - vec[2] * math.sin(theta_r))
    ret_vec.append(vec[1])
    ret_vec.append(vec[0] * math.sin(theta_r) - vec[2] * math.cos(theta_r))
    
    return ret_vec

def add(v1: list, v2:list):
    return [v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2]]

TAGS_CORNERS_LOCATIONS = {i: [add(TAGS_CENTERS_LOCATIONS[i], rotate_around_y(v, TAGS_ROTATIONS[i])) for v in TAG_SHAPE] for i in TAGS_CENTERS_LOCATIONS.keys()} # this is the dict that tells you for each tag where each of its corners is located in field coords


LIMELIGHT_FOV_W =  59.6 
LIMELIGHT_FOV_H = 45.7 

LIMELIGHT_FOCAL_LENGTH = (math.tan(math.radians(LIMELIGHT_FOV_W))*2*math.tan(math.radians(LIMELIGHT_FOV_H))*2)**0.5 