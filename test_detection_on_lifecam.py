import math
import gbvision as gbv
import numpy as np
import april_tags_utils as ap
import settings
import show_on_field



def main():
    # np.set_printoptions(7)
    cam = gbv.USBCamera(1, gbv.LIFECAM_3000)
    cam.set_exposure(-7)
    F_LENGTH = (math.tan(0.4435563306578366)*2*math.tan(0.3337068395920225)*2)**0.5 
    # this part for trying undistortion
    matrix = np.array([[661.92113903,   0.        , 307.48134487],
                       [  0.        , 662.86886862, 231.33037259],
                       [  0.        ,   0.        ,   1.        ]])
    distortion = np.array([[ 1.63258818e-01, -1.29538370e+00, -2.96528789e-03,
         1.11106656e-03,  2.31431665e+00]])
    show_on_field.thread.start()
    win = gbv.FeedWindow("window")
    
    while True:
        ok, frame = cam.read()
        frame = ap.undistort_frame(frame, matrix, distortion)
        all_c_3d, ids = ap.process_frame(frame, settings.TAG_SIDE_LENGTH, F_LENGTH)
        all_rotations = [ap.get_tag_rotation(corners, 0.5 * (corners[0]+corners[2]))[0] for corners in all_c_3d]
        try:
            show_on_field.xyz = np.array(settings.TAGS_CENTERS_LOCATIONS[ids[0][0]])-np.array(
                                        ap.rotate(0.5 * (all_c_3d[0][0]+all_c_3d[0][2]),
                                          0.5*math.pi-all_rotations[0][0],
                                          0,#-all_rotations[0][1],
                                          0))#-all_rotations[0][2]))
            show_on_field.rotation = all_rotations[0][0]
        except:
            pass
        
        
        
        frame = ap.draw_tags(frame, all_c_3d, F_LENGTH, settings.TAG_SIDE_LENGTH)
        win.show_frame(frame)
        
if __name__ == '__main__':
    main()
    