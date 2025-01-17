from ultralytics import YOLO
import cv2
import os
import time
from torchvision import transforms
import matplotlib.pyplot as plt
import torch
import numpy as np
import warnings
warnings.filterwarnings('ignore') 

from models.experimental import attempt_load 
from utils.datasets import letterbox 
from utils.general import non_max_suppression_kpt, xywh2xyxy
from utils.plots import output_to_keypoint, plot_skeleton_kpts, plot_one_box

# set gpu device if possible
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print('Device:', device)

output_dir = "C:\\Python projects\\yolov7\\result"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def show_image(img, figsize=(6,6)):            
    plt.figure(figsize=figsize)
    plt.imshow(img)
    plt.axis('off')
    time_now = int(time.time())
    output_photo_path1 = os.path.join(output_dir, f"output_image_{time_now}.png")
    plt.savefig(output_photo_path1)


def plot_pose_prediction(img : cv2.Mat, pred : list, thickness=2, 
                         show_bbox : bool=True) -> cv2.Mat:
    bbox = xywh2xyxy(pred[:,2:6])
    for idx in range(pred.shape[0]):
        plot_skeleton_kpts(img, pred[idx, 7:].T, 3)
        if show_bbox:
            plot_one_box(bbox[idx], img, line_thickness=thickness)

def process_video(input_path, output_path):
    # Open the input video file and extract its properties
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # Create VideoWriter object 
    out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))
    #  Processing a video file frame by frame
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            pred = make_pose_prediction(model, frame)
            plot_pose_prediction(frame, pred, show_bbox=False)
            out.write(frame)
            cv2.imshow('Pose estimation', frame)
        else:
            break

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    # Release VideoCapture and VideoWriter
    cap.release()
    out.release()
    # Close all frames and video windows
    cv2.destroyAllWindows()

def pose_estimation_video(filename, out_filename):
    # Open the input video file and extract its properties 
    cap = cv2.VideoCapture(filename)
    tot = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    i = 0.
    while cap.isOpened():
        print(f"Processing: {i/tot:.1%}", end='\r' )
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pred = make_pose_prediction(model, frame)
        else:
            break
        i += 1.
    cap.release()


def scale_pose_output(output, resized_shape:tuple, original_shape:tuple, is_padded:bool=True):
    ''' Scale yolo pose estimator output coordinates of bbox and keypoints
    from `resized_shape` to `original_shape` 
    '''
    scaled_output = output.copy()
    scale_ratio = (resized_shape[1] / original_shape[1], 
                   resized_shape[0] / original_shape[0])      
    if is_padded:
        # remove padding
        pad_scale = min(scale_ratio)
        padding = (resized_shape[1] - original_shape[1] * pad_scale ) / 2, (
                   resized_shape[0] - original_shape[0] * pad_scale ) / 2
        scale_ratio = (pad_scale, pad_scale)
        
        scaled_output[:, 2] -= padding[0]     # x_c unpadding
        scaled_output[:, 3] -= padding[1]     # y_c unpadding
        scaled_output[:, 7::3] -= padding[0]  # x_kpts unpadding
        scaled_output[:, 8::3] -= padding[1]  # y_kpts unpadding
    
    scaled_output[:, [2, 4]] /= scale_ratio[0]
    scaled_output[:, [3, 5]] /= scale_ratio[1]
    scaled_output[:, 7::3] /= scale_ratio[0]
    scaled_output[:, 8::3] /= scale_ratio[1]

    return scaled_output

def make_pose_prediction(model, img : cv2.Mat) -> list:
    ''' Make prediction with yolo pose estimator `model` on image `img`
    '''
    # Resize and pad image while meeting stride-multiple constraints
    img_ = letterbox(img, 960, stride=64, auto=True)[0]
    resized_shape = img_.shape[0:2]
    # Transform image to model readable structure
    img_ = transforms.ToTensor()(img_)
    img_ = torch.tensor(np.array([img_.numpy()]))
    img_ = img_.to(device).float()
    with torch.no_grad():
        output, _ = model(img_)
    # Filter predictions
    output = non_max_suppression_kpt(output, 0.25, 0.65, 
                                     nc=model.yaml['nc'], 
                                     nkpt=model.yaml['nkpt'], 
                                     kpt_label=True)
    output = output_to_keypoint(output)
    # scale to original image shape
    output = scale_pose_output(output, resized_shape, img.shape[0:2])
    return output

while True:
    model_choice = input("Выберите модель: 1 - своя, 2 - предобученная YOLO : ")
    if model_choice == "1":
        model_path = input("Введите путь к вашей модели: ")
        if os.path.exists(model_path):
            try:
                model = YOLO(model_path)
                class_dict = model.names
                all_classes = list(class_dict.values())
                break
            except Exception as e:
                print(f"Ошибка при загрузке модели {e}")
        else:
            print("Указанный путь не существует")

    elif model_choice == "2":
        model_choice2 = input("Выберите модель: 1 - YOLO11N, 2 - YOLOv7 : ")
        if model_choice2 == '1':
            try:
                model = YOLO("C:\Python projects\yolov7\models\yolo11n.pt")
                class_dict = model.names
                all_classes = list(class_dict.values())
                break
            except Exception as e:
                print(f"Ошибка при загрузке модели {e}")
        elif model_choice2 == '2':
            try: 
                model = attempt_load('C:\Python projects\yolov7\weights\yolov7-w6-pose.pt', map_location=device) 
                model.eval()
                all_classes = model.yaml['nc'], model.yaml['nkpt']
                print('Number of classes:', model.yaml['nc'])
                print('Number of keypoints:', model.yaml['nkpt'])
                while True:
                    source_choice3 = input("Выберите источник: 1 - камера, 2 - видео, 3 - изображение: ")
                    if source_choice3 == "1":
                        # Open the input video file and extract its properties
                        time_now = int(time.time())
                        output_video_path = os.path.join(output_dir, f"output_video_{time_now}.mp4")

                        cap = cv2.VideoCapture(0)
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
                        # Create VideoWriter object 
                        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
                        #  Processing a video file frame by frame
                        while cap.isOpened():
                            ret, frame = cap.read()
                            if ret:
                                pred = make_pose_prediction(model, frame)
                                plot_pose_prediction(frame, pred, show_bbox=False)
                                out.write(frame)
                                cv2.imshow('Pose estimation', frame)
                            else:
                                break

                            if cv2.waitKey(10) & 0xFF == ord('q'):
                                break
                        # Release VideoCapture and VideoWriter
                        cap.release()
                        out.release()
                        # Close all frames and video windows
                        cv2.destroyAllWindows()
                        if not cap:
                            print("Не удалось открыть камеру")
                            continue
                        break

                    elif source_choice3 == "2":
                        input_path = input("Введите путь к видеофайлу")
                        if os.path.exists(input_path):
                            time_now = int(time.time())
                            output_video_path = os.path.join(output_dir, f"output_video_{time_now}.mp4")
                            process_video(input_path, output_video_path)

                            if not cap:
                                print("Не удалось прочитать видеофайл")
                                continue
                            break
                        else:
                            print("Указанный путь к видео не существует")

                    elif source_choice3 == "3":
                        image_path = input("Введите путь к изображению")
                    
                        if os.path.exists(image_path):
                            cap = None
                            img = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
                            pred = make_pose_prediction(model, img)
                            plot_pose_prediction(img, pred, show_bbox=True)
                            show_image(img, (18,18))
                            break
                        else:
                            print("Указанный путь к изображению не существует")

                    else:
                        print("Некорректный ввод, попробуйте 1, 2 или 3")
                    
                        # if source_choice == "1" or source_choice == "2":
                        #     if cap.isOpened():
                        #         frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        #         frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        #         fps = cap.get(cv2.CAP_PROP_FPS)

                        #         time_now = int(time.time())
                        #         output_video_path = os.path.join(output_dir, f"output_video_{time_now}.mp4")
                        #         fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                        #         out = cv2.VideoWriter(
                        #             output_video_path, fourcc, fps, (frame_width, frame_height)
                        #         )

                        # while cap is not None and cap.isOpened():
                        #     ret, frame = cap.read()
                        #     if not ret:
                        #         break

                        #     results = model.predict(source=frame, conf=0.4)
                        #     frame = results[0].plot()

                        #     cv2.imshow("Video", frame)

                        #     if source_choice == "1" or source_choice == "2":
                        #         out.write(frame)

                        #     if cv2.waitKey(30) == 27:
                        break



            except Exception as e:
                print(f"Ошибка при загрузке модели {e}")
    else:
        print("Некорректный ввод, попробуйте 1 или 2")

print("Доступные классы", all_classes)

while True:
    mode_choice = input("Выберите режим: 1 - детекция, 2 - сегментация: ")
    if mode_choice == "1":
        mode = "detection"
        break
    elif mode_choice == "2":
        mode = "segmentation"
        if model_choice == "2":
            model = YOLO("models/yolo11n-seg.pt")
        break
    else:
        print("Некорректный ввод, попробуйте 1 или 2")

while True:
    source_choice = input("Выберите источник: 1 - камера, 2 - видео, 3 - изображение: ")
    if source_choice == "1":
        cap = cv2.VideoCapture(0)
        if not cap:
            print("Не удалось открыть камеру")
            continue
        break

    elif source_choice == "2":
        video_path = input("Введите путь к видеофайлу")
        if os.path.exists(video_path):
            cap = cv2.VideoCapture(video_path)
            if not cap:
                print("Не удалось прочитать видеофайл")
                continue
            break
        else:
            print("Указанный путь к видео не существует")

    elif source_choice == "3":
        image_path = input("Введите путь к изображению")
        if os.path.exists(image_path):
            cap = None
            break
        else:
            print("Указанный путь к изображению не существует")

    else:
        print("Некорректный ввод, попробуйте 1, 2 или 3")

if source_choice == "1" or source_choice == "2":
    if cap.isOpened():
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        time_now = int(time.time())
        output_video_path = os.path.join(output_dir, f"output_video_{time_now}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(
            output_video_path, fourcc, fps, (frame_width, frame_height)
        )

while cap is not None and cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model.predict(source=frame, conf=0.4)
    frame = results[0].plot()

    cv2.imshow("Video", frame)

    if source_choice == "1" or source_choice == "2":
        out.write(frame)

    if cv2.waitKey(30) == 27:
        break

if source_choice == "3" and cap is None:
        image = cv2.imread(image_path)
        results = model.predict(source=image, conf=0.4,show=True)
        image = results[0].plot()
        time_now = int(time.time())
        output_photo_path = os.path.join(output_dir, f"output_image_{time_now}.jpg")
        cv2.imwrite(output_photo_path, image)
        cv2.waitKey(0)
cv2.destroyAllWindows()
