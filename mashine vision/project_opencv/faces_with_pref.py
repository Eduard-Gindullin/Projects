# Программа для определния лиц с настройками
import cv2

cascade_src = 'cascades/haarcascade_frontalface_alt2.xml'
face_cascade = cv2.CascadeClassifier(cascade_src)

face_img = cv2.imread('src/2.jpg')
gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)

cv2.namedWindow("Detected Faces")

min_scale_factor = 101
prev_scale_factor = min_scale_factor
prev_neighbors = 1
prev_min_size = 30


def nothing(x):
    pass

cv2.createTrackbar("Scale", 'Detected Faces', min_scale_factor, 300, nothing)
cv2.createTrackbar("Neighbors", 'Detected Faces', 1, 20, nothing)
cv2.createTrackbar("Min size", 'Detected Faces', 30, 150, nothing)

def detected_faces(scale_factor, min_neighbors, min_size):
    display_image = face_img.copy()
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=(min_size, min_size)
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(display_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    cv2.imwrite("src/Detecte_with_per.jpg", display_image)
    cv2.imshow("Detected Faces", display_image)

detected_faces(min_scale_factor / 100.0, prev_neighbors, prev_min_size )

while True:
    scale_factor = cv2.getTrackbarPos("Scale", 'Detected Faces')
    min_neighbors = cv2.getTrackbarPos("Neighbors", 'Detected Faces')
    min_size = cv2.getTrackbarPos("Min size", "Detected Faces")

    if scale_factor < min_scale_factor:
        scale_factor = min_scale_factor
        cv2.setTrackbarPos("Scale", 'Detected Faces', min_scale_factor)

    if (scale_factor != prev_scale_factor or 
        min_neighbors != prev_neighbors or 
        min_size != prev_min_size):

        prev_scale_factor = scale_factor
        prev_neighbors = min_neighbors
        prev_min_size = min_size

        detected_faces(scale_factor / 100.0, min_neighbors, min_size)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()