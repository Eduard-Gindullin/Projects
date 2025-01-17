# Программа для определения машин по видео
import cv2

cascade_src = 'cascades/cars.xml'
car_cascade = cv2.CascadeClassifier(cascade_src)

video_src = 'src/video_cars1.avi'
video_src = 'src/video_cars2.avi'

capture_src = cv2.VideoCapture(video_src)

while True:
    ret = capture_src.read()
    if ret[0]:
        cap = ret[1]
    else:
        break

    gray = cv2.cvtColor(cap, cv2.COLOR_BGR2GRAY)

    cars = car_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2)

    for (x, y, w, h) in cars:
        cv2.rectangle(cap, (x, y), (x + w, y + h), (0, 255, 255),2)
    
    cv2.imshow('video', cap)

    if cv2.waitKey(30) == 27:
        break

cv2.destroyAllWindows()