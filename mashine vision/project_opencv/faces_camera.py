# Программа для распознавания лица с камеры

import cv2

cascade_src = 'cascades/haarcascade_frontalface_alt2.xml'
cascade_faces = cv2.CascadeClassifier(cascade_src)

cap = cv2.VideoCapture(1) # 0 или 1 или 2 получение изображения с камеры
while True:
    ret = cap.read()
    if ret[0]:
        capture = ret[1]
    else:
        break

    gray = cv2.cvtColor(capture, cv2.COLOR_BGR2GRAY)

    faces = cascade_faces.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        cv2.rectangle(capture, (x, y), (x + w, y + h), (0, 255, 255), 2)

    cv2.imshow('video', capture)
    if cv2.waitKey(33) == 27:
        break
    
cv2.destroyAllWindows()