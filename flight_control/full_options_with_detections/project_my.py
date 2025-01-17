import tkinter as tk
from tkinter import filedialog, messagebox
import rospy
from clover import srv
from std_srvs.srv import Trigger
import math
import json
import numpy as np
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from PIL import Image as PILImage, ImageTk
from datetime import datetime
import threading
import csv
from clover.srv import SetLEDEffect
from sensor_msgs.msg import Range
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

rospy.init_node('fligth_control_gui')

bridge = CvBridge()
fullbody_cascade = cv2.CascadeClassifier("haarcascade_fullbody.xml")
background_sub = cv2.createBackgroundSubtractorMOG2()

latest_image = None
running_mode = None
lock = threading.Lock()
video_writer = None
flight_plan = None
current_range = None

get_telemetry = rospy.ServiceProxy("get_telemetry", srv.GetTelemetry)
navigate = rospy.ServiceProxy("navigate", srv.Navigate)
navigate_global = rospy.ServiceProxy("navigate_global", srv.NavigateGlobal)
land = rospy.ServiceProxy("land", Trigger)
set_effect = rospy.ServiceProxy('led/set_effect', SetLEDEffect, persistent=True)

start = get_telemetry()
home_possion = [start.lat, start.lon]
flag = True
# Открытие csv документа
def load_data():
    file_path = filedialog.askopenfilename(title="Выберите файл", filetypes=(("CSV файлы ", "*.csv"), ("Все файлы", "*.*")))
    if not file_path:
        return [], []
    
    times = []
    heights = []

    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        header = next(reader)
        for col in reader:
            try:
                time = datetime.strptime(col[0], "%Y-%m-%d_%H-%M-%S")
                height = float(col[3])
                times.append(time)
                heights.append(height)
            except Exception as e:
                
                continue     
    return times, heights

# Построение графика
def plot_graph():
    times, heights = load_data()
    if not times or not heights:
        status_label.config(text="Ошибка: данный не загружены или файл пуст.")
        return
    
    fig, ax = plt.subplots(figsize=(2, 2))

    start_time = times[0]

    times_in_seconds = []

    for t in times:
        time_diff = t - start_time
        times_in_seconds.append(time_diff.total_seconds())
    
    ax.plot(times_in_seconds, heights, label="График высоты")
    ax.set_xlabel("Время")
    ax.set_ylabel("Высота")
    ax.legend()
    # plt.show()
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().place(x=800,y=50)


# Получение данных о расстоянии
def range_callback(msg):
    global current_range
    current_range = msg.range

rospy.Subscriber('rangefinder/range', Range, range_callback)

# Обновление данных о расстоянии
def update_range_label():
    if current_range is not None:
        range_label.config(text=f"Расстояние: {current_range:.2f} м")
    else:
        range_label.config(text="Расстояние: Неизвестно")

    window.after(1000, update_range_label)
# Включение светодиода
def turn_on_led():
    try:
        set_effect(effect='rainbow_fill')
    except:
        status_label.config(text="Ошибка включения светодиода")

# Создание файла csv
def create_telemetry_csv():
    time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"telemetry_{time}.csv"

    with open(filename, mode="w", newline='') as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(['Time', 'X', 'Y', 'Z','Lat','Lon', 'Speed'])
    return filename

# Запись телеметрии
def record_telemetry_to_csv(filename):
    try:
        telem = get_telemetry()
        with open(filename, mode="a", newline='') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(
                [datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), 
                telem.x, 
                telem.y, 
                telem.z,
                telem.lat,
                telem.lon,
                math.sqrt(telem.vx ** 2+ telem.vy**2+ telem.vz**2)]
                )
    except Exception as e:
        status_label.config(text=f"Ошибка записи телеметрии {e}")

# Функция начала записи телеметрии
def start_telemetry_recording():
    global telemetry_filename
    csv_telem_button.config(text="Остановить")
    telemetry_filename = create_telemetry_csv()
    
    def record_telemetry():
        while True:
            record_telemetry_to_csv(telemetry_filename)
            rospy.sleep(5)
            
    threading.Thread(target=record_telemetry, daemon=True).start()
    
# Обновление высоты
def update_altitude():
    try:
        telem = get_telemetry()
        altitude = telem.z
        alt_label.config(text=f"Текущая высота {altitude:.2f} м")
    except:
        alt_label.config(text="Ошибка получения высоты")

    window.after(1000, update_altitude)

def arrival_wait(tolerance=0.2):
    while not rospy.is_shutdown():
        telem = get_telemetry(frame_id="navigate_target")
        if math.sqrt(telem.x**2 + telem.y**2 +telem.z**2 ) < tolerance:
            break
        rospy.sleep(0.2)

# Взлет
def takeoff():
    try:
        if entry_z.get():
            z = float(entry_z.get())
        else:
            z = 3
        if entry_speed.get():
            speed = float(entry_speed.get())
        else:
            speed = 1.0
        x = 0
        y = 0
        yaw = float('nan')
        frame_id = "body"
        auto_arm = True
        threading.Thread(target=navigate, args=(x, y, z, yaw, speed, frame_id, auto_arm)).start()
        status_label.config(text=f"Взлет на высоту {z} м со скоростью {speed} м/с")
        
    except:
        status_label.config(text="Ошибка: введите числовые значения для высоты и скорости")

# Посадка
def land_drone():
    threading.Thread(target=land).start()
    status_label.config(text="Дрон приземлился")

# Полет по локальным координатам
def fly_to_local_coodinates():
    try:
        x = float(entry_x.get())
        y = float(entry_y.get())
        if entry_z.get():
            z = float(entry_z.get())
        else:
            z = 0
        if entry_speed.get():
            speed = float(entry_speed.get())
        else:
            speed = 1.0
        yaw = float('nan')
        frame_id = "body"
        auto_arm = True
        threading.Thread(navigate(x, y, z, yaw, speed, frame_id, auto_arm)).start()
        status_label.config(text=f"X: {x}, Y: {y}, высота {z} и скорость {speed}")
    except:
        status_label.config(text="Ошибка: введите числовые значения для  X, Y, высоты и скорости")

# Полет по кнопкам
def fly_by_buttons_forward():
        x = 1
        y = 0
        z = 0
        if entry_speed.get():
            speed = float(entry_speed.get())
        else:
            speed = 1.0
        yaw = float('nan')
        frame_id = "body"
        auto_arm = True
        threading.Thread(navigate(x, y, z, yaw, speed, frame_id, auto_arm)).start()
        status_label.config(text=f"X: {x}, Y: {y}, высота {z} и скорость {speed}")

def fly_by_buttons_backward():
        x = -1
        y = 0
        z = 0
        if entry_speed.get():
            speed = float(entry_speed.get())
        else:
            speed = 1.0
        yaw = float('nan')
        frame_id = "body"
        auto_arm = True
        threading.Thread(navigate(x, y, z, yaw, speed, frame_id, auto_arm)).start()
        status_label.config(text=f"X: {x}, Y: {y}, высота {z} и скорость {speed}")

def fly_by_buttons_right():
        x = 0
        y = 0
        z = 0
        if entry_speed.get():
            speed = float(entry_speed.get())
        else:
            speed = 1.0
        yaw = float(30)
        frame_id = "body"
        auto_arm = True
        threading.Thread(navigate(x, y, z, yaw, speed, frame_id, auto_arm)).start()
        status_label.config(text=f"X: {x}, Y: {y}, высота {z} и скорость {speed}")

def fly_by_buttons_left():
        x = 0
        y = 0
        z = 0
        if entry_speed.get():
            speed = float(entry_speed.get())
        else:
            speed = 1.0
        yaw = float(-30)
        frame_id = "body"
        auto_arm = True
        threading.Thread(navigate(x, y, z, yaw, speed, frame_id, auto_arm)).start()
        status_label.config(text=f"X: {x}, Y: {y}, высота {z} и скорость {speed}")

def fly_by_buttons_up():
        x = 0
        y = 0
        z = 1
        if entry_speed.get():
            speed = float(entry_speed.get())
        else:
            speed = 1.0
        yaw = float('nan')
        frame_id = "body"
        auto_arm = True
        threading.Thread(navigate(x, y, z, yaw, speed, frame_id, auto_arm)).start()
        status_label.config(text=f"X: {x}, Y: {y}, высота {z} и скорость {speed}")

def fly_by_buttons_down():
        x = 0
        y = 0
        z = -1
        if entry_speed.get():
            speed = float(entry_speed.get())
        else:
            speed = 1.0
        yaw = float('nan')
        frame_id = "body"
        auto_arm = True
        threading.Thread(navigate(x, y, z, yaw, speed, frame_id, auto_arm)).start()
        status_label.config(text=f"X: {x}, Y: {y}, высота {z} и скорость {speed}")

# Полет по глобальным координатам
def fly_to_global_coordinates():
    try:
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())
        if entry_z.get():
            z = float(entry_z.get())
        else:
            z = 3.0
        if entry_speed.get():
            speed = float(entry_speed.get())
        else:
            speed = 1.0
        threading.Thread(target=navigate_global, args=(lat, lon, z, speed, 1, "map", False)).start()
        status_label.config(text=f"Широта: {lat}, Долгота: {lon}")
    except:
        status_label.config(text="Ошибка: введите числовые значения для  широты, долготы, высоты и скорости")

#Возврат на начальную точку
def fly_home():
    if home_possion:
        if entry_z.get():
            z = float(entry_z.get())
        else:
            z = 3.0
        if entry_speed.get():
            speed = float(entry_speed.get())
        else:
            speed = 1.0
        lat, lon = home_possion[0], home_possion[1]
        threading.Thread(target=navigate_global, args=(lat, lon, z, speed, 1, "map", False)).start()
        status_label.config(text="Возвращаемся домой")
        land()
    else:
        status_label.config(text="Ошибка: точка взлета не определена")
        return

# Показ телеметрии
def show_telemetry():
    telem = get_telemetry()
    status_label.config(text=f"X = {telem.x}, Y = {telem.y}, Z = {telem.z}")


# Загрузка плана
def load_plan_file(filename):
    with open(filename, "r") as file:
        return json.load(file)

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Flight Plan Files", "*.plan")])
    if filename:
        if filename.endswith(".plan"):
            try:
                global flight_plan
                flight_plan = load_plan_file(filename)
                status_label.config(text=f"Файл плана полета {filename} успешно загружен")
            except:
                messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить план полета {filename}")
        else:
            messagebox.showerror("Неверный файл", "Выберите файл с расширением .plan")

# Полет по плану
def fly_by_plan():
    if flight_plan is None:
        messagebox.showerror("Ошибка", "План полета не загружен")
        return
    def run_flight_plan():
        home_lat = flight_plan["mission"]["plannedHomePosition"][0]
        home_lon = flight_plan["mission"]["plannedHomePosition"][1]
        
        for item in flight_plan["mission"]["items"]:
            command = item["command"]
            if command == 22:
                if get_telemetry().armed:
                    navigate_global(lat=home_lat, lon=home_lon, z=3, yaw= math.inf, speed=1, frame_id='map')
                    arrival_wait()
                    land()
                else:
                    z = item["params"][6]
                    navigate_global(lat=home_lat, lon=home_lon, z=z, yaw= math.inf, speed=1, frame_id='map', auto_arm=True)
                    navigate_global(lat=home_lat, lon=home_lon, z=z, yaw= math.inf, speed=1, frame_id='map')
                    arrival_wait()
            elif command == 16:
                lat = item["params"][4]
                lon = item["params"][5]
                navigate_global(lat=lat, lon=lon, z=z, yaw= math.inf, speed=1, frame_id='map')
                arrival_wait()
            elif command == 20:
                navigate_global(lat=home_lat, lon=home_lon, z=z, yaw= math.inf, speed=1, frame_id='map')
                arrival_wait()
            elif command == 21:
                land()
        status_label.config(text="План полета завершен")        
    threading.Thread(target=run_flight_plan).start()

# Обработка и вывод изображения с камеры
def camera_image(msg):
    global latest_image
    with lock:
        latest_image = bridge.imgmsg_to_cv2(msg, 'bgr8')

image_sub = rospy.Subscriber('main_camera/image_raw', Image, camera_image, queue_size=1)

# Обновление изображения в Tkinter
def update_image():
    if latest_image is not None:
        with lock:
            img_rgb = cv2.cvtColor(latest_image, cv2.COLOR_BGR2RGB)
            img_pil = PILImage.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(image=img_pil)

            camera_label.config(image=img_tk)
            camera_label.image=img_tk
    window.after(100, update_image)

# Распознание объекта с каскадом
def detected_objects():
    global latest_image
    while running_mode == "objects":
        with lock:
            if latest_image is None:
                continue
            img = latest_image.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        objects = fullbody_cascade.detectMultiScale(gray, scaleFactor = 1.05, minNeighbors=4, minSize=(30,30))

        for (x, y, w, h) in objects:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        display_image(img)

# Запуск режима распознания объектов с каскадом
def start_object_detection():
    stop_detection()
    global running_mode
    running_mode = "objects"
    threading.Thread(target=detected_objects, daemon=True).start()


# Остановка распознания
def stop_detection():
    global running_mode
    running_mode = None

# Распознание движущихся объектов
def detect_motion():
    global latest_image
    while running_mode == "motion":
        with lock:
            if latest_image is None:
                continue
            img = latest_image.copy()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = background_sub.apply(gray)
        _, thresh = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 400:
                cv2.polylines(img, [contour], isClosed=True, color=(0, 0, 255), thickness=1)
        display_image(img)

# Распознание объектов по цвету
def detect_by_color():
    global latest_image
    while running_mode == "color_detection":
        with lock:
            if latest_image is None:
                continue
            img = latest_image.copy()
        
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 100, 50])
        upper_green = np.array([85, 255, 255])
        lower_blue = np.array([100, 150, 50])
        upper_blue = np.array([140, 255, 255])        

        green_mask = cv2.inRange(hsv_img, lower_green, upper_green)
        blue_mask = cv2.inRange(hsv_img, lower_blue, upper_blue)

        green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in green_contours:
            if cv2.contourArea(contour) > 200:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        for contour in blue_contours:
            if cv2.contourArea(contour) > 200:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        display_image(img)
       
# Запуск режима распознания по цветам
def start_detect_color():
    stop_detection()
    global running_mode
    running_mode = "color_detection"
    print("start")
    threading.Thread(target=detect_by_color, daemon=True).start()

# Заупуск режима распознавания движущихся объектов
def start_motion_detection():
    stop_detection()
    global running_mode
    running_mode = "motion"
    threading.Thread(target=detect_motion, daemon=True).start()


# Отображение видео
def display_image(img):
    global video_writer
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = PILImage.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)

    camera_label.config(image=img_tk)
    camera_label.image=img_tk

    if video_writer is not None:
        video_writer.write(img)

# Старт записи видео
def start_video_recording():
    global video_writer
    if video_writer is not None:
        messagebox.showinfo("Запись", "Видео уже записывается")
        return
    
    time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"output_{time}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(filename, fourcc, 30.0, (320, 240))

    def record():
        global latest_image
        while video_writer is not None:
            with lock:
                if latest_image is None:
                    continue
                video_writer.write(latest_image)
            rospy.sleep(0.03)
    threading.Thread(target=record, daemon=True).start()

# Остановка записи видео
def stop_video_recording():
    global video_writer
    if video_writer is not None:
        video_writer = None
        messagebox.showinfo("Запись", "Видео успешно сохранено")

# Окно
window = tk.Tk()
window.title("Управление дроном")
window.geometry("1080x550")

# Поля ввода и лейблы
tk.Label(window, text="Высота взлета (м): ").grid(row=0, column=0, padx=20, pady=10)
entry_z = tk.Entry(window,width=10)
entry_z.grid(row=0,column=1)

tk.Label(window, text="Координата X (м): ").grid(row=1, column=0, padx=20, pady=10)
entry_x = tk.Entry(window, width=10)
entry_x.grid(row=1, column=1)

tk.Label(window, text="Координата Y (м): ").grid(row=2, column=0, padx=20, pady=10)
entry_y = tk.Entry(window, width=10)
entry_y.grid(row=2, column=1)

tk.Label(window, text="Широта: ").grid(row=3, column=0, padx=20, pady=10)
entry_lat = tk.Entry(window, width=10)
entry_lat.grid(row=3, column=1)

tk.Label(window, text="Долгота: ").grid(row=4, column=0, padx=20, pady=10)
entry_lon = tk.Entry(window, width=10)
entry_lon.grid(row=4, column=1)

tk.Label(window, text="Скорость (м/с): ").grid(row=5, column=0, padx=20, pady=10)
entry_speed = tk.Entry(window, width=10)
entry_speed.grid(row=5, column=1)

# Кнопки управления
takeoff_button = tk.Button(window, text="Взлет", width=20, bg="brown3", fg="white", relief="solid", command=takeoff).grid(row=6,column=0,padx=20, pady=5)
land_button = tk.Button(window, text="Посадка", width=20, relief="solid", command=land).grid(row=7, column=0, padx=20,pady=5)
global_coordinates_button = tk.Button(window, text="Гл. Координаты", width=20, relief="solid",command=fly_to_global_coordinates).grid(row=8, column=0, padx=20, pady=5)
# flip_button = tk.Button(window, text="Флип", width=20, relief="solid").grid(row=9, column=0, padx=20, pady=5)
load_plan_button = tk.Button(window, text="Загрузить план", width=20, relief="solid",command=browse_file).grid(row=10, column=0, padx=20, pady=5)
home_button = tk.Button(window, text="Домой", width=20, relief="solid", command=fly_home).grid(row=6, column=1, padx=20, pady=5)
telemetry_button = tk.Button(window, text="Телеметрия", width=20, relief="solid",command=show_telemetry).grid(row=7, column=1, padx=20, pady=5)
local_coordinates = tk.Button(window, text="Лок. Координаты", width=20, relief="solid",command=fly_to_local_coodinates).grid(row=8, column=1, padx=20, pady=5)
activate_plan = tk.Button(window, text="Активировать план", width=20, relief="solid", command=fly_by_plan).grid(row=10, column=1, padx=20, pady=5 )
# Кнопки управления полетом
button_forward = tk.Button(window, text="Вперед", width=20, relief="solid", command=fly_by_buttons_forward).grid(row=1, column=4, padx=20, pady=5)
button_backward = tk.Button(window, text="Назад", width=20, relief="solid", command=fly_by_buttons_backward).grid(row=2, column=4, padx=20, pady=5)
button_left = tk.Button(window, text="Влево", width=20, relief="solid", command=fly_by_buttons_left).grid(row=3, column=4, padx=20, pady=5)
button_right = tk.Button(window, text="Вправо", width=20, relief="solid", command=fly_by_buttons_right).grid(row=4, column=4, padx=20, pady=5)
button_up = tk.Button(window, text="Вверх", width=20, relief="solid", command=fly_by_buttons_up).grid(row=5, column=4, padx=20, pady=5)
button_down = tk.Button(window, text="Вниз", width=20, relief="solid", command=fly_by_buttons_down).grid(row=6, column=4, padx=20, pady=5)

status_label = tk.Label(window, text="Состояние дрона", fg="blue")
status_label.grid(row=11, column=0, columnspan=2)
alt_label = tk.Label(window, text="Текущая высота", fg="blue")
alt_label.grid(row=11, column=3, columnspan=2)

range_label = tk.Label(window, text="Текущая расстояние", fg="green")
range_label.grid(row=12, column=3, columnspan=2)

# Кнопки для камеры
detection_button = tk.Button(window, text="Распознать объект", width=20, bg="blue", fg="white", relief="solid",command=start_object_detection).grid(row=7, column=3, padx=20, pady=5)
detection_move_button = tk.Button(window, text="Распознать движение", width=20, bg="blue", fg="white", relief="solid", command=start_motion_detection).grid(row=8, column=3, padx=20, pady=5)
detection_color_button = tk.Button(window, text="Распознать цвета", width=20, bg="blue", fg="white", relief="solid", command=start_detect_color).grid(row=9, column=3, padx=20, pady=5)
stop_detection_button = tk.Button(window, text="Остановить", width=20, bg="red", fg="white", relief="solid",command=stop_detection).grid(row=10, column=3, padx=20, pady=5)
video_record_button = tk.Button(window, text="Записать видео", width=20, bg="green", fg="white", relief="solid", command=start_video_recording).grid(row=7, column=4, padx=20, pady=5)
stop_video_record_button = tk.Button(window, text="Остановить запись", width=20, bg="red", fg="white", relief="solid",command=stop_video_recording).grid(row=8, column=4, padx=20, pady=5)

camera_label = tk.Label(window)
camera_label.grid(row=0, column=3, rowspan=8)

# Кнопка телеметрии
csv_telem_button = tk.Button(window, text="Запись телеметрии", width=20, bg="blue", fg="white", relief="solid", command=start_telemetry_recording)
csv_telem_button.grid(row=12, column=0, columnspan=2, padx=20, pady=5)

led_button = tk.Button(window, text="Светодиод", width=20, bg="yellow", fg="black", relief="solid", command=turn_on_led).grid(row=9, column=4, columnspan=2, padx=20, pady=5)

plot_button = tk.Button(window, text="Построить график", width=20, bg="silver", fg="black", relief="solid", command=plot_graph).grid(row=10, column=4, columnspan=2, padx=20, pady=5)

window.after(100, update_image)
window.after(1000, update_altitude)
update_range_label()
window.mainloop()
