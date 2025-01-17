# Программа для определения номера на машине
import cv2

cascade_src = 'cascades/haarcascade_russian_plate_number.xml'
car_cascade = cv2.CascadeClassifier(cascade_src)

car_img = cv2.imread('src/3.jpg')

gray = cv2.cvtColor(car_img, cv2.COLOR_BGR2GRAY)

car_plates = car_cascade.detectMultiScale(gray, scaleFactor=1.01, minNeighbors=8, minSize=(30, 30))

for (x, y, w, h) in car_plates:
    cv2.rectangle(car_img, (x, y), (x + w, y + h), (255, 0, 0), 2)

cv2.imshow("Detected Plates", car_img)
cv2.imwrite("src/Detected_plates.jpg", car_img)
cv2.waitKey(0)
cv2.destroyAllWindows()