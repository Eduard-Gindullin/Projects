# Программа для определения лиц
import cv2

cascade_src = 'cascades/haarcascade_frontalface_default.xml'
cascade_src_alt = 'cascades/haarcascade_frontalface_alt.xml'
cascade_src_alt2 = 'cascades/haarcascade_frontalface_alt2.xml'
cascade_src_alt_3 = 'cascades/haarcascade_frontalface_alt_tree.xml'

faces_cascade = cv2.CascadeClassifier(cascade_src)
faces_cascade_alt= cv2.CascadeClassifier(cascade_src_alt)
faces_cascade_alt2 = cv2.CascadeClassifier(cascade_src_alt2)
faces_cascade_alt3 = cv2.CascadeClassifier(cascade_src_alt_3)

faces_img = cv2.imread('src/2.jpg')

gray = cv2.cvtColor(faces_img, cv2.COLOR_BGR2GRAY)

faces_default = faces_cascade.detectMultiScale(gray, scaleFactor=1.01, minNeighbors=1, minSize=(30,30), 
                                               maxSize=(43,43))

faces_alt = faces_cascade_alt.detectMultiScale(gray, scaleFactor=1.01, minNeighbors=1, minSize=(30,30),
                                               maxSize=(43,43))

faces_alt2 = faces_cascade_alt2.detectMultiScale(gray, scaleFactor=1.01, minNeighbors=1, minSize=(30,30),
                                               maxSize=(43,43))

faces_alt3 = faces_cascade_alt3.detectMultiScale(gray, scaleFactor=1.01, minNeighbors=1, minSize=(30,30),
                                               maxSize=(43,43))

# for (x, y, w, h) in faces_default:
#     cv2.rectangle(faces_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

# for (x, y, w, h) in faces_alt:
#     cv2.rectangle(faces_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

# for (x, y, w, h) in faces_alt2:
#     cv2.rectangle(faces_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

for (x, y, w, h) in faces_alt3:
    cv2.rectangle(faces_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

cv2.imshow("Default_faces", faces_img)
cv2.imwrite("src/Alt3_faces.jpg", faces_img)
cv2.waitKey(0)
cv2.destroyAllWindows()