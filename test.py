import limelight_code
import gbvision as gbv
if __name__ == '__main__':
    cam = gbv.USBCamera(1, gbv.LIFECAM_3000) 
    cam.set_exposure(-9)
    ok, frame = cam.read()
    win = gbv.FeedWindow("window")
    raw = gbv.FeedWindow("raw")
    while True:
        raw.show_frame(frame)
        l, frame, li = limelight_code.runPipeline(frame, [])
        win.show_frame(frame)
        
        ok, frame = cam.read()
        