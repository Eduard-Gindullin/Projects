import rospy
from clover import srv
from std_srvs.srv import Trigger
import math
import json
import csv

from map_drawing import create_map, update_light_path, save_map

rospy.init_node('drone_control')

get_telemetry = rospy.ServiceProxy('get_telemetry',srv.GetTelemetry)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
navigate_global = rospy.ServiceProxy('navigate_global', srv.NavigateGlobal)
land = rospy.ServiceProxy('land', Trigger)



        

# Ожидаем прибытие дрона к целевой позиции
def wait_arrival(tolerance = 0.2):
    while not rospy.is_shutdown():
        telem = get_telemetry(frame_id='navigate_target')
        if math.sqrt(telem.x**2 + telem.y**2+ telem.z**2) < tolerance:
            return
        rospy.sleep(0.2)

# Загружаем план полета
def load_plan_file(filename):
    with open(filename, 'r') as file:
        plan = json.load(file)
    return plan

# Взлет с параметрами
def takeoff(navigate, map_drone, drone_position, telemetry):
    z_flight = float(input('Укажите желаемую высоту полета (в метрах): \n'))
#    speed = float(input('Укажите скорость взлета : \n'))
    print(f"Высота полета будет {z_flight} метра(ов)" )
    print(f"Взлет на высоту {z_flight} метра(ов)")
    navigate(x = 0, y = 0, z = z_flight, frame_id = 'body', auto_arm = True)
    wait_arrival()
    print("Дрон взлетел")



    telem = get_telemetry(frame_id = "body")
    drone_position.append((telem.lat, telem.lon))
    telemetry.append((telem.lat, telem.lon, telem.alt, z_flight))
    update_light_path(map_drone, drone_position)
     
    return map_drone, drone_position, telemetry

# Посадка
def land_drone(land, map_drone, drone_position, telemetry):
    print("Приземляемся...")
    land()
    print("Дрон приземлился")

    telem = get_telemetry(frame_id = "body")
    drone_position.append((telem.lat, telem.lon))
    update_light_path(map_drone, drone_position)
    telemetry.append((telem.lat, telem.lon, telem.alt, 0))
    
    return map_drone, drone_position

# Полет по локальным координатам
def fly_to_local_coordinates(navigate, map_drone, drone_position, telemetry):
    x = float(input("Введите координаты X (метры): "))
    y = float(input("Введите координаты Y (метры): "))
    speed_flight = float(input('Укажите желаемую скрость полета: \n'))
    z_flight = float(input('Укажите желаемую высоту полета (в метрах): \n'))
    print(f"Скорость полета составит {speed_flight} на высоте {z_flight} ")
    print(f"Полет в точку X={x}, Y={y}")
    navigate(x = x, y = y, z = z_flight, frame_id = 'body', speed = speed_flight)
    wait_arrival()
    print("Дрон достиг точки по локальным координатам")

    telem = get_telemetry(frame_id = "body")
    drone_position.append((telem.lat, telem.lon))
    update_light_path(map_drone, drone_position)
    telemetry.append((telem.lat, telem.lon, telem.alt, z_flight))
    return map_drone, drone_position

# Полет по глобальным координатам
def fly_to_global_coordinates(navigate_global, map_drone, drone_position, telemetry):
    lat = float(input("Введите широту: "))
    lon = float(input("Введите долготу: "))
    speed_flight = float(input('Укажите желаемую скрость полета: \n'))
    z_flight = float(input('Укажите желаемую высоту полета (в метрах): \n'))
    print(f"Скорость полета составит {speed_flight} на высоте {z_flight} ")
    print(f"Полет в точку: Latitude={lat}, Longitude={lon}")
    navigate_global(lat = lat, lon = lon, z = z_flight, yaw = math.inf, speed = speed_flight)
    wait_arrival()
    print("Дрон достиг точки по глобальным координатам")

    telem = get_telemetry(frame_id = "body")
    drone_position.append((telem.lat, telem.lon))
    update_light_path(map_drone, drone_position)
    telemetry.append((telem.lat, telem.lon, telem.alt, z_flight))
    return map_drone, drone_position

# Запись домашней позиции
def record_home_position():
    telem = get_telemetry(frame_id = "body")
    home_position = (telem.lat, telem.lon)
    print(f"Домашняя позиция: Latitude={home_position[0]}, Longitude={home_position[1]}")
    return home_position

# Возврат на домашнюю позицию
def return_to_home(navigate_global, home_position, map_drone, drone_position, telemetry):
    speed_flight = float(input('Укажите желаемую скрость полета: \n'))
    print(f"Скорость полета составит {speed_flight} ")
    lat = home_position[0]
    lon = home_position[1]
    print(f"Возвращаемся на домашнюю позицию: Latitude={lat}, Longitude={lon}")
    navigate_global(lat = lat, lon = lon, z = 3, yaw = math.inf, speed = speed_flight)
    wait_arrival()
    print("Дрон вернулся на домашнюю позицию")

    telem = get_telemetry(frame_id = "body")
    drone_position.append((telem.lat, telem.lon))
    update_light_path(map_drone, drone_position)
    telemetry.append((telem.lat, telem.lon, telem.alt, 3))
    return map_drone, drone_position

# Полет по плану полета
def fly_by_plan(navigate_global, land, map_drone, drone_position, telemetry):
    filename = input("Введите имя файла плана полета (например, plan.plan): ")
    speed_flight = float(input('Укажите желаемую скрость полета: \n'))
    print(f"Скорость полета составит {speed_flight} ")
    plan = load_plan_file(filename)
    for item in plan['mission']['items']:
        command = item['command']
        if command == 16:
            lat = item['params'][4]
            lon = item['params'][5]
            alt = item['params'][6]
            print(f"Полет в точку: Latitude={lat}, Longitude={lon}")
            navigate_global(lat = lat, lon = lon, z = 3, yaw = math.inf, speed = speed_flight)
            wait_arrival()

            drone_position.append((lat, lon))
            telemetry.append((lat, lon, alt, 3))
            update_light_path(map_drone, drone_position)
        elif command == 20:
            home_lat = plan['mission']['plannedHomePosition'][0]
            home_lon = plan['mission']['plannedHomePosition'][1]
            navigate_global(lat = home_lat, lon = home_lon, z = 3, yaw = math.inf, speed = speed_flight)
            wait_arrival()

            drone_position.append((home_lat, home_lon))
            update_light_path(map_drone, drone_position)
        elif command == 21:
            land()
            print("Дрон успешно приземлился")
            return False

# Основной цикл управления
def main():

    is_flying = False
    home_position = record_home_position()

    drone_map = create_map()
    drone_position =[]
    telemetry =[]

    while True:
        print("\nВыберите действие:")
        print("1. Взлет (высота 3 метра)")
        print("2. Приземление")
        print("3. Полет по локальным координатам")
        print("4. Полет по глобальным координатам")
        print("5. Возврат на домашнюю позицию")
        print("6. Полет по плану полета")
        print("0. Выход")

        choice = input("Введите номер действия: ")

        if choice == '1':
            if not is_flying:
                drone_map, drone_position, telemetry = takeoff(navigate, drone_map, drone_position, telemetry)
                is_flying = True
            else:
                print("Дрон уже в воздухе")
        elif choice == '2':
            if is_flying:
                drone_map, drone_position = land_drone(land, drone_map, drone_position, telemetry)
                is_flying = False
            else:
                print("Дрон уже на змеле")
        elif choice == '3':
            if is_flying:
                drone_map, drone_position = fly_to_local_coordinates(navigate, drone_map, drone_position, telemetry)
            else:
                print("Сначала нужно взлететь")
        elif choice == '4':
            if is_flying:
                drone_map, drone_position = fly_to_global_coordinates(navigate_global, drone_map, drone_position, telemetry)
            else:
                print("Сначала нужно взлететь")
        elif choice == '5':
            if is_flying:
                drone_map, drone_position = return_to_home(navigate_global, home_position, drone_map, drone_position, telemetry)
        elif choice == '6':
            if is_flying:
                is_flying, drone_map, drone_position = fly_by_plan(navigate_global, land,drone_map, drone_position, telemetry)
            else:
                print("Сначала нужно взлететь")
        elif choice == '0':
            print("Выход из программы")
            if is_flying:
                drone_map, drone_position, land_drone(land, drone_map, drone_position, telemetry)
            save_map(drone_map)
            print(telemetry)
            with open('telemetry.csv', mode = 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['latitude', 'longitude', 'altitude', 'z in meters1'])
                writer.writerows(telemetry)
            break
        else:
            print("Неверный код команды")

main()