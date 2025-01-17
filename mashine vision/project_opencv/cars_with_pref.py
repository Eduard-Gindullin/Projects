# Программа для распознания машин с настройками
import cv2

cascade_src = 'cascades/cars.xml'
cars_cascade = cv2.CascadeClassifier(cascade_src)

video_src = 'src/video_cars1.avi'
video = cv2.VideoCapture(video_src)

cv2.namedWindow("Cars with Preference")

def nothing(x):
    pass

min_scale_factor = 10

cv2.createTrackbar("Scale", "Cars with Preference", min_scale_factor, 300, nothing)
cv2.createTrackbar("Min Neighbors", "Cars with Preference", 1, 25, nothing)
cv2.createTrackbar("Min Size", "Cars with Preference", 30, 70, nothing)

while True:
    ret = video.read()
    if ret[0]:
        cap = ret[1]
    else:
        break

    gray = cv2.cvtColor(cap, cv2.COLOR_BGR2GRAY)

    scale_factor = cv2.getTrackbarPos("Scale", "Cars with Preference")

    if scale_factor < min_scale_factor:
        scale_factor = min_scale_factor
        cv2.setTrackbarPos("Scale", "Cars with Preference", min_scale_factor)

    min_neighbors = cv2.getTrackbarPos("Min Neighbors", "Cars with Preference")
    min_size = cv2.getTrackbarPos("Min Size", "Cars with Preference")

    cars = cars_cascade.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=(min_size, min_size)
    )

    for (x, y, w, h) in cars:
        cv2.rectangle(cap, (x, y), (x + w, y + h), (0, 255, 255), 2)
    
    cv2.imshow("Cars with Preference", cap)

    if cv2.waitKey(30) == 27:
        break

cv2.destroyAllWindows()
