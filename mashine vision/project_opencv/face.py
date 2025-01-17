# Для распознавания лица
import cv2

cascade_src = "cascades/haarcascade_frontalface_default.xml"

face_cascade = cv2.CascadeClassifier(cascade_src)

face_img = cv2.imread('src/1.jpg')

gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)

faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=1, minSize=(150, 150))

for (x,y, w, h) in faces:
    cv2.rectangle(face_img,(x,y),(x + w, y + h), (255, 0, 0), 2)

cv2.imshow('Face_detected', face_img)
cv2.imwrite('src/Face_detected.jpg', face_img)
cv2.waitKey(0)
cv2.destroyAllWindows()