import cv2

def load_cascade(object_type):
    cascades = {
        "cars" : "cascades/cars.xml",
        "peoples" : "cascades/pedestrian.xml",
        "face" : "cascades/haarcascade_frontalface_alt2.xml"
    }
    return cv2.CascadeClassifier(cascades[object_type])



object_type = input("Введите тип объекта для обнаружения (cars, peoples, face): ")
video_source = input("Введите путь до файла, или 'camera' для использования камеры: ")

cascade = load_cascade(object_type)


output_video = "src/output_video.avi"


if video_source == "camera":
    cap = cv2.VideoCapture(1)
else:
    cap = cv2.VideoCapture(video_source)

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))
while True:
    ret = cap.read()
    if ret[0]:
        img = ret[1]
    else:
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    objects = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2)

    for (x, y, w, h) in objects:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
    
    cv2.imshow("Video", img)

    out.write(img)

    if cv2.waitKey(30) == 27:
        break

cv2.destroyAllWindows()
    