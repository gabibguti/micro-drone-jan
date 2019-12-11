#C:\Users\micro2\Downloads\micro-drone-jan-testaCamera\drone
from cv2 import *
from datetime import datetime, timedelta
import os
# from mov_drone import *
from tello import Tello
from time import sleep
from threading import Timer
from threading import Thread
import math
from simple_functions import *

# GLOBALS
LIGHT_BLUE = (90, 50, 38)
DARK_BLUE = (150, 255, 255)
FOUND_NEW_TAG = False
TAG_COUNTER = 0
CURR_DIR = os.getcwd()
PICS_DIR = os.path.join(CURR_DIR, "tag-pics")
DRONE_TIMEOUT = 7
curr_state = None
MAX_UP_MOVEMENTS = 10
UP_MOVEMENTS = 0
CURR_TAG_DATA = {"x": 0, "y": 0}
CURR_IMG_DATA = {"x": 0, "y": 0}
UPDATE_TAG = False
TOTAL_DIFF_TOLERANCE = 130
WIDTH_DIFF_TOLERANCE = 60
HEIGHT_DIFF_TOLERANCE = 100


# LOGS
def log_drone_battery():
    global timer
    if drone is not None:
        print("Battery", drone.state["bat"])
        drone.read_tof
    timer = Timer(5,log_drone_battery)
    timer.start()

def log_drone_state():
    global state_timer
    wait_sec = 3
    if curr_state:
        print("Drone's current state is: ", curr_state)
    state_timer = Timer(wait_sec,log_drone_state)
    state_timer.start()

# UTILS

def calculateDistance(x1,y1,x2,y2):
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
     return dist

def delete_picture_files():
    for tag_picture in os.listdir(PICS_DIR):
        os.remove(os.path.join(PICS_DIR,tag_picture))

def save_tag_img(img, tag_id):
    tag_img_label = "tag" + str(tag_id)
    print("Taking Picture... {}".format(tag_img_label))
    tag_path = os.path.join(PICS_DIR, tag_img_label + ".png")
    imwrite(tag_path, img)

# IMAGE TREATMENT

def is_square(w, h):
    # A square will have an aspect ratio that is approximately equal to one, otherwise, the shape is a rectangle
    ar = w / float(h)
    if ar >= 0.95 and ar <= 1.05: # Its a Square
        return True
    else: # its a Rectangle
        return False

# DRONE MOVEMENT
def iniciar_drone():
    global drone
    drone.inicia_cmds()
    sleep(DRONE_TIMEOUT)
    drone.takeoff()
    sleep(DRONE_TIMEOUT)

def para():
    global drone
    drone.land()
    sleep(DRONE_TIMEOUT)
    drone = None

def dentro_regiao():
    global xDif
    global yDif
    if (xDif > -100) and (xDif < 100):
        if (yDif > -100) and (yDif < 100):
                return True
    return False

def centralizaDrone():
    velX = 0
    velZ = 0
    if (xDif < -100):
        velX = 10
    elif (xDif > 100):
        velX = -10
    if (yDif < -100):
        velZ = 10
    elif (yDif > 100):
        velZ = -10
    drone.rc(velX, 0, velZ, 0)

def threaded_function(arg, arg2):
    global FOUND_NEW_TAG, CURR_TAG_DATA, CURR_IMG_DATA, UPDATE_TAG
    global imagem
    global final_img
    global curr_state
    global TAG_COUNTER

    # TODO: Ajustar valores de tolerancia (depende do tamanho da nossa area azul a ser capturada, a que distancia elas \
    #  serao capturadas, espacamento entre cada quadrado azul na prateleira)
    #xTol = 125
    xTol = 75
    yTol = 75

    # Melhorias rect verde
    area_limit = 3000
    show_rect = False
    counter_no_rect = 0
    COUNTER_LIMIT = 250

    # NOTE: Primeiro estado eh de achar uma tag, assumimos que o drone esta alinhado horizontalmente com a tag e so precisa ir para cima
    curr_state = "find_first_tag"
    LIGHT_BLUE = (90, 150, 0)
    DARK_BLUE = (150, 255, 255)

    COUNT_NONES = 0
    DISCONNECT_TOL = 50

    tag_dict = {"blueX":0, "blueY":0, "blueW":0, "blueH":0}

    detection_tolerance = timedelta(seconds=5)
    last_detect = datetime.now()

    while True:
        if drone is None and test_mode != 3:
            print("Drone has disconected...")
            COUNT_NONES+=1
            if COUNT_NONES >= DISCONNECT_TOL:
                break
            continue

        blue_img, mascara = apply_mask(imagem, LIGHT_BLUE, DARK_BLUE)
        blue_img_height = blue_img.shape[0]
        blue_img_width  = blue_img.shape[1]
        img_center_x = int(blue_img_width / 2)
        img_center_y = int(blue_img_height / 2)
        contornos, _ = findContours(mascara, RETR_TREE, CHAIN_APPROX_SIMPLE)

        if len(contornos) != 0:
            contornos.sort(key=contourArea ,reverse=True) # ordena da maior a menor area
            for contorno in contornos:
                peri = arcLength(contorno, True)
                approx = approxPolyDP(contorno, 0.04 * peri, True)
                # if the shape has 4 vertices, it is either a square or a rectangle
                if len(approx) == 4:
                    # compute the bounding box of the contour and use the bounding box to compute the aspect ratio
                    (x, y, w, h) = boundingRect(approx)
                    if w * h >= area_limit:

                        tag_dict['blueX'] = x
                        tag_dict['blueY'] = y
                        tag_dict['blueW'] = w
                        tag_dict['blueH'] = h

                        show_rect = True
                        counter_no_rect = 0

                        tag_center_x = x + w / 2
                        tag_center_y = y + h / 2

                        if(not FOUND_NEW_TAG):
                            FOUND_NEW_TAG = True
                            # save tag and image data
                            CURR_TAG_DATA["x"] = tag_center_x
                            CURR_TAG_DATA["y"] = tag_center_y
                            CURR_IMG_DATA["x"] = img_center_x
                            CURR_IMG_DATA["y"] = img_center_y
                            # add green rectangle to identify tag (blue square)
                            rectangle(blue_img, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 0), thickness=3)
                            # save image on local folder
                            TAG_COUNTER += 1
                            save_tag_img(blue_img, TAG_COUNTER)
                        elif(UPDATE_TAG):
                            UPDATE_TAG = False
                            # save tag and image data
                            CURR_TAG_DATA["x"] = tag_center_x
                            CURR_TAG_DATA["y"] = tag_center_y
                            CURR_IMG_DATA["x"] = img_center_x
                            CURR_IMG_DATA["y"] = img_center_y
                            # add green rectangle to identify tag (blue square)
                            rectangle(blue_img, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 0), thickness=3)
                            # save image on local folder
                            save_tag_img(blue_img, TAG_COUNTER)

                        break
                    else:
                        counter_no_rect += 1
                        break

        if counter_no_rect >= COUNTER_LIMIT:
            show_rect = False

        if show_rect:
            rectangle(blue_img, pt1=(tag_dict['blueX'], tag_dict['blueY']),
                      pt2=(tag_dict['blueX'] + tag_dict['blueW'],
                           tag_dict['blueY'] + tag_dict['blueH']),
                      color=(0, 255, 0), thickness=3)

        # update thread image stream
        final_img = blue_img.copy()

        if kill_thread:
            break
    print("Thread died")


######## Movimentacao do Drone ###########################################################
routine_states = [
    "find_first_tag", # go up until find a tag
    "centralize", # right after finding a tag, centrilze drone
    "wait",
    "detect_qr_code",
    "process_qr_code",
    "find_next_tag", # after processing the QR Code move right until find another tag
    "goto_next_floor", # go up OR down after scanned all tags from one level
    "turnoff"
]

def movement_drone(x, y, z, k):
    if(test_mode == 1):
        drone.rc(x, y, z, k)

def mov_drone_recorrente():
    global FOUND_NEW_TAG, UP_MOVEMENTS, MAX_UP_MOVEMENTS, UPDATE_TAG
    global timer_mov_drone
    global curr_state
    global new_tag_found

    function_timeout = 0.5

    if drone is not None:

        if curr_state == "find_first_tag":
            print("UP_MOVEMENTS: {}".format(UP_MOVEMENTS))
            if(FOUND_NEW_TAG and len(os.listdir(PICS_DIR)) > 0): #when we have a tag picture try to centralize
                print("FOUNT TAG!")
                FOUND_NEW_TAG = False
                UP_MOVEMENTS = 0

                curr_state = "wait"

            if(UP_MOVEMENTS < MAX_UP_MOVEMENTS):
                UP_MOVEMENTS += 1
                movement_drone(0, 0, 10, 0) # try going up
                function_timeout = 4
            else:
                curr_state = "turnoff" # give up

        elif curr_state == "wait":
            function_timeout = 4
            movement_drone(0, 0, 0, 0)
            # calculate where to go
            dist = calculateDistance(CURR_IMG_DATA["x"], CURR_IMG_DATA["y"], CURR_TAG_DATA["x"], CURR_TAG_DATA["y"])
            diff_x = abs(CURR_TAG_DATA["x"] -  CURR_IMG_DATA["x"])
            diff_y = abs(CURR_TAG_DATA["y"] -  CURR_IMG_DATA["y"])
            print("Distance from tag to center:", dist, " * ", diff_x, " * ", diff_y)

            if (dist < TOTAL_DIFF_TOLERANCE):
                movement_drone(0, 0, 0, 0)
                UPDATE_TAG = False
                curr_state = "detect_qr_code"
            else:
                curr_state = "centralize"

        elif curr_state == "centralize":
            function_timeout = 4
            diff_x = abs(CURR_TAG_DATA["x"] -  CURR_IMG_DATA["x"])
            diff_y = abs(CURR_TAG_DATA["y"] -  CURR_IMG_DATA["y"])

            moveX = 0
            moveZ = 0
            if(diff_x > WIDTH_DIFF_TOLERANCE):
                if(CURR_TAG_DATA["x"] > CURR_IMG_DATA["x"]): # go left
                    moveX = 5
                else: # go right
                    moveX = -5
            elif(diff_y > HEIGHT_DIFF_TOLERANCE):
                if(CURR_TAG_DATA["y"] < CURR_IMG_DATA["y"]): # go up
                    moveZ = 5
                else: # go down
                    moveZ = -5

            print("drone going: left/right: {} up/down: {}".format(moveX, moveZ))
            movement_drone(moveX, 0, moveZ, 0)

            UPDATE_TAG = True

            # go back to wait
            curr_state = "wait"

#            if dentro_regiao():
#                curr_state = "detect_qr_code"
#            else:
#                centralizaDrone()

        elif curr_state == "detect_qr_code":
            curr_state = "process_qr_code"

        elif curr_state == "process_qr_code":
            curr_state = "find_next_tag"

        elif curr_state == "find_next_tag":
            print("UP_MOVEMENTS: {}".format(UP_MOVEMENTS))
            if :  # when we have a tag picture try to centralize
                print("FOUNT TAG!")
                FOUND_NEW_TAG = False
                UP_MOVEMENTS = 0

                curr_state = "wait"

            if (UP_MOVEMENTS < MAX_UP_MOVEMENTS):
                UP_MOVEMENTS += 1
                movement_drone(0, 0, 10, 0)  # try going up
                function_timeout = 4
            else:
                curr_state = "turnoff"  # give up
            if new_tag_found:
                curr_state = "centralize"
                new_tag_found = False
            else:
                movement_drone(7, 0, 0, 0)

        elif curr_state == "turnoff":
            para()

        else:
            # Transition State, do nothing
            pass

    timer_mov_drone = Timer(function_timeout, mov_drone_recorrente) # 500 ms
    timer_mov_drone.start()

kill_thread = False
new_tag_found = False

if __name__ == '__main__':

    test_mode = 1 # camera drone, com voo
    # test_mode = 2 # camera drone, sem voo
    # test_mode = 3  # camera pc, sem drone

    # Create empty folder to store tag pictures
    if not os.path.exists(PICS_DIR):
        os.makedirs(PICS_DIR)
    else:
        delete_picture_files()

    # TODO: Ajustar valores de tolerancia (depende do tamanho da nossa area azul a ser capturada, a que distancia elas \
    #  serao capturadas, espacamento entre cada quadrado azul na prateleira)
    xTol = 125
    yTol = 75

    # TODO: ajustar intervalo de tolerancia entre cada deteccao
    last_detect = datetime.now()
    DETECTION_TOLERANCE = timedelta(seconds=0.5)
    area_limit = 3000
    isAdjusting = False

    # Drone Vars
    drone_x = 10
    last_mov = datetime.now()
    timer_drone = datetime.now()
    drone_tolerance = timedelta(seconds=3)
    drone_end = datetime.now() + timedelta(seconds=50)

    # Drone start
    if test_mode != 3:
        #drone = Tello("TELLO-C7AC08", test_mode=False)
        drone = Tello("TELLO-D023AE", test_mode=False)
        drone.inicia_cmds()
        sleep(DRONE_TIMEOUT)

        if test_mode == 1:
            drone.takeoff()
            sleep(DRONE_TIMEOUT)

        # Time nao morre
        timer = Timer(5, log_drone_battery)
        timer.start()

    if test_mode != 3:
        # Timer moves
        timer_mov_drone = Timer(0.1, mov_drone_recorrente)
        timer_mov_drone.start()

    # State machine timer
    state_timer = Timer(1.5,log_drone_state)
    state_timer.start()

    # First capture to initialize thread
    if test_mode == 3:
        drone = None
        stream = VideoCapture(0)
        _, imagem = stream.read()
    else:
        imagem = drone.current_image
    final_img = imagem.copy()

    thread = Thread(target=threaded_function, args=(5, 2,))
    thread.start()

    while True:
        if test_mode == 3:
            _, imagem = stream.read()
        else:
            imagem = drone.current_image

        # imshow("Main Vison", imagem)
        imshow("Thread Vison", final_img)
        # Mostra a imagem durante 1 milissegundo e interrompe loop quando tecla q for pressionada
        if waitKey(20) & 0xFF == ord("q"):
            break

    kill_thread = True
    thread.join()
    if test_mode == 3:
        stream.release()
        destroyAllWindows()

