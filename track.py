# Import packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import imutils
from config import *
from shapely.geometry import Point


# Init camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

camera.brightness = 50
camera.contrast = 10
camera.video_stabilization = True
camera.exposure_mode = 'off'
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

#mqtt and restart the counters
send_message()

# Camera warmup
time.sleep(0.1)

# Capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # Grab the raw NumPy array representing the image
    image = frame.array
    image = imutils.resize(image, width=400, height=400)
    #get the point 
    cv2.setMouseCallback('Frame',obtener_punto)

    #draw entry and exit areas
    draw(image)

    #image processing
    blobs = cv2.GaussianBlur(image, (5,5), 0)                           # Blur (noise reduction)
    blobs = cv2.cvtColor(blobs, cv2.COLOR_BGR2GRAY)                     # Convert to grayscale
    fgmask = fgbg.apply(blobs)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
    fgmask = cv2.dilate(fgmask,None,iterations=2)
    img, contours,hierarchy = cv2.findContours(fgmask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)


    for cnt in contours:
        if cv2.contourArea(cnt) > 300:
            x,y,w,h = cv2.boundingRect(cnt)
            x1 = w/2
            y1 = h/2
            cx = x+x1
            cy = y +y1
            epsilon = (x1+y1)/2
            area = cv2.contourArea(cnt)
            cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
            area = cv2.contourArea(cnt)
            point = Point(cx,cy)
            #entry area
            for zona in inList:
                if zona[2].contains(point) == True:
                    if Vehicules.comparison_state(cx,cy) or Vehicules.comparison_move(epsilon,cx,cy):
                        Vehicules.update_minimo_1(epsilon,cx,cy)
                    else:
                        crear_nuevo(area,zona[0],400,800,cx,cy)
            #update
            if Vehicules.comparison_state(cx,cy) or Vehicules.comparison_move(epsilon,cx,cy):
                Vehicules.update_minimo_1(epsilon,cx,cy)

            #exit area
            for zona in outList:
                if zona[2].contains(point) == True:
                    try:
                        entrada, salida, tipo = Vehicules.asignar_salida_cercano(epsilon,zona[0],cx,cy)
                        add_count(lista,entrada,salida,tipo)
                        print entrada,salida,tipo
                    except:
                        pass

            #dynamic text
            cv2.putText(image,"status: {}".format(centroid), (cx,cy),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    
    # Show the frame
    cv2.putText(image,"#cars: {}".format(Vehicules.getAll()), (10,10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(image,"counter: {}".format(Vehicules.next_id), (10,50),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.imshow("Frame", image)
    cv2.imshow("fgmask", fgmask)
    
    # Clear stream in preparation for the next frame
    rawCapture.truncate(0)

    # Exit loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
