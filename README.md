# 2023-vision

how to use on limelight:
* to put the actual vision code on the limelight go to the limelights python editor and copy paste the code there
* be sure to edit code in limelight_code.py and copy to limelight python editor as copying from the limelight python editor makes it crash somehow
* choosing a threshold:
    - take a picture of what you want to track and save it as "thr.jpg" in this folder
    - run limelight_median_thr.py and mark the object you want to track using the cursor
    - look at the resulting image to see if you like it, if not try again
* Main.java reads the (x, y, z) values (sent in this format) exactly as the robot would, you can use it to see the values being sent
* uploading new libraries: 
    - to upload libraries use sftp, you can use FileZila
    - host: 10.71.12.11 (limelights IP)| username: root | password: 7112| port: 22 (sftp standard)
    - once connected go to usr/lib/python3.9/site-packages and upload the folder or file there

important notes / conventions:
* ports:
    - 5800 - the port where you send the robot's current location using UDP, the limelight sends the data and the robot recieves it, data is sent in this format (x, y, z) all floats
    - 5801 - the port where you send the locations of all game pieces to the simulation
    - 5802 - the port where you send the location of the locked on reflector from the limelight to the robot
    - 5804 - the port where the robot sends his current location and rotation to the simulation
* all measurements are and should always be in meters
* constant physical values should be changed in april_tags.py
* (x, y, z) raw readings (direct calculations relative only to the camers) go like this: 
    - x - the axis that is parallel to the camera and is parallel to the width of the frame
    - y - the axis that is parallel to the camera and is parallel to the height of the frame
    - z - the axis that determines depth, it is perpendicualr to the camera
    - (0, 0, 0) is the point that appears exactly in the middle of the frame that is exactly at the pinhole of the camera
* (x, y, z) robot coordinates / field coordinates:
    - x - the axis parallel to the 2 wide sides of the fields boundaries
    - y - the axis that represents height from the carpet, perpendicualr to the floor
    - z - the axis parallel to the 2 shorter boundaries of the field
    - (0, 0, 0) is the point exactly in the middle of the field exactly on the carpet

