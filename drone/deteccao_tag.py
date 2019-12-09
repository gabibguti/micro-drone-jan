#C:\Users\micro2\Downloads\micro-drone-jan-testaCamera\drone
from cv2 import *
from datetime import datetime, timedelta
import os
# from mov_drone import *
from extra.tello import Tello
from time import sleep
from threading import Timer
from threading import Thread

def para():
    drone.land()

def mov_dronee(x, y, z, w):
    drone.goto(int(x), int(y), int(z), int(w))

def dentro_regiao():
    global xDif
    global yDif
    # print("[REG] x:{}, y:{}, h:{}, l:{}, area:{}\n".format(xReg, yReg, wReg, hReg, areaRef))
    if (xDif > -100) and (xDif < 100):
        if (yDif > -100) and (yDif < 100):
                return True
    return False


def movHoriz(xRef, xReg):
    xDist = (xReg-xRef)*4/3
    drone.goto(int(xDist)*10,0,0,10)
    sleep(drone_interval)

def movVert(yRef, yReg):
    zDist = (yReg-yRef)*4/3
    drone.goto(0, 0, int(zDist)*10, 10)
    sleep(drone_interval)

def centralizaDrone():
    #drone.goto(0,0,0,10)
    #sleep(drone_interval)
    #print("\t[DIF] xDif:{}, yDif:{}".format(xDif, yDif))
    #drone.goto(0,30,0,10)
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


    #movHoriz(xRef, xReg)
    #if (xDif > 5) or (xDif < -5):
    #   movHoriz(xRef, xReg)
    #if yDif != 0:
    #   movVert(yRef, yReg)
    #print("test")
    #isAdjusting = False


def decola():
    a = 7
    drone.takeoff()
    sleep(drone_interval)

def is_square(w, h):
    # A square will have an aspect ratio that is approximately equal to one, otherwise, the shape is a rectangle
    ar = w / float(h)
    if ar >= 0.95 and ar <= 1.05: # Its a Square
        return True
    else: # its a Rectangle
        return False

def is_new_square(x, xRef, y, yRef, tol):
    xTol = tol
    yTol = tol
    if (x > xRef - xTol and x < xRef + xTol) and (y > yRef - yTol and y < yRef + yTol):
        return False
    return True

def delete_picture_files():
    for tag_picture in os.listdir(pics_dir):
        os.remove(os.path.join(pics_dir,tag_picture))

def take_picture(img, xRef, yRef, xTol, wRef, hRef):
    global tag_counter
    print("\n\tTaking Picture! (At: {})".format(datetime.now()))
    print("\t[NEW] x:{}, y:{}, w:{}, h:{}, area:{}".format(xRef, yRef, wRef, hRef, wRef * hRef))
    print("\t[IMG] tam_x:{}, tam_y:{}, img:{}".format(imagem.shape[1], imagem.shape[0], imagem.shape))
    print("\n\t\t\t[COUNTER] ", tag_counter)
    tag_picture = os.path.join(pics_dir, "tag" + str(tag_counter + 1) + ".png")
    if not os.path.exists(tag_picture):
        imwrite(tag_picture, img)
        tag_counter += 1



def threaded_function(arg, arg2):
    global imagem
    global final_img
    global found_first_tag
    
    global xRef
    global yRef
    global wRef
    global hRef
    global xDif
    global yDif
    
    global curr_state

    # TODO: Ajustar valores de tolerância (depende do tamanho da nossa área azul a ser capturada, a que distância elas \
    #  serão capturadas, espaçamento entre cada quadrado azul na prateleira)
    #xTol = 125
    xTol = 75
    yTol = 75
    
    # TODO: ajustar intervalo de tolerancia entre cada detecção
    detection_tolerance = timedelta(seconds=5)
    last_detect = datetime.now()
    area_limit = 6000
    
    # NOTE: Primeiro estado eh de achar uma tag, assumimos que o drone esta alinhado horizontalmente com a tag e so precisa ir para cima
    curr_state = "find_first_tag" 
    
    while True:        
        # If no picture taken, then no tag found yet
        if curr_state == "find_first_tag" and len(os.listdir(pics_dir)) > 0:
            curr_state = "centralize"
        
        # Parte 1
        imagem_hsv = cvtColor(imagem, COLOR_BGR2HSV)
        mascara = inRange(imagem_hsv, light_blue, dark_blue)
        imagem1 = bitwise_and(imagem, imagem, mask=mascara)

        # Parte 2
        mascara2 = bitwise_not(mascara)
        graybgr = cvtColor(imagem, COLOR_BGR2GRAY)
        graybgr = cvtColor(graybgr, COLOR_GRAY2BGR)
        imagem2 = bitwise_and(graybgr, graybgr, mask=mascara2)

        # Parte 3
        blue_img = addWeighted(graybgr, 1, imagem1, 1, 0)

        # FIXME: Versoes diferentes do OpenCV podem causar problemas aqui na "findContours" (nesse caso foi utilizada a versão 3)
        contornos, _ = findContours(mascara, RETR_TREE, CHAIN_APPROX_SIMPLE)
        area = 0
        
        xOld = xRef
        yOld = yRef
        hOld = hRef
        wOld = wRef
        if len(contornos) != 0:
            contornos.sort(key=contourArea ,reverse=True) # ordena da maior a menor area
            for contorno in contornos:
                peri = arcLength(contorno, True)
                approx = approxPolyDP(contorno, 0.04 * peri, True)
                # if the shape has 4 vertices, it is either a square or a rectangle
                if len(approx) == 4:
                    # compute the bounding box of the contour and use the bounding box to compute the aspect ratio
                    (x, y, w, h) = boundingRect(approx)
                    # TODO: Ajustar valor de "area_limit"
                    if is_square(w, h) and w * h >= area_limit:                        
                        xRef = x
                        yRef = y
                        wRef = w
                        hRef = h
                        area = w * h
                        xMid = int(blue_img.shape[1] / 2)
                        yMid = int(blue_img.shape[0] / 2)
                        xReg = (xMid - wRef/2)
                        yReg = (yMid - hRef/2)
                        xDif = xReg - xRef
                        yDif = yRef - yReg
                        break
        
        #if last_detect > datetime.now():
        img_no_green_rect = blue_img.copy()
        rectangle(blue_img, pt1=(xRef, yRef), pt2=(xRef + wRef, yRef + hRef), color=(0, 255, 0), thickness=3)
        
        if is_new_square(xRef, xOld, yRef, yOld, xTol) and last_detect < datetime.now():
            new_tag_found = True ## CHECK HERE
            take_picture(blue_img, xRef, yRef, xTol, wRef, hRef)
            last_detect = datetime.now() + detection_tolerance  # starts timer
            
            # todo delete test:
            #if curr_state != "find_next_tag":
            #    curr_state = "find_next_tag"
            #elif new_tag_found == True:
            #    curr_state = "detect_qr_code"
            
        if last_detect > datetime.now():
            final_img = blue_img.copy()
        else:
            final_img = img_no_green_rect.copy()
        
        if kill_thread:
            break
    print("Thread died")


######## Movimentacao do Drone ###########################################################
routine_states = ["find_first_tag", # go up until find a tag
                  "centralize", # right after finding a tag, centrilze drone
                  "detect_qr_code",
                  "process_qr_code",
                  "find_next_tag", # after processing the QR Code move right until find another tag
                  "goto_next_floor" # go up OR down after scanned all tags from one level
                  ]
curr_state = None
refPic = None
xRef = 0
yRef = 0
wRef = 0
hRef = 0
xDif = 0
yDif = 0

def nao_morre():
    global timer
    if drone is not None:
        print("Batery", drone.state["bat"])
        drone.read_tof
    timer = Timer(5,nao_morre)
    timer.start()

def print_state():
    global state_timer
    wait_sec = 3
    if curr_state:    
        print("Drone's current state is: ", curr_state)
        if curr_state == "find_first_tag":
            print("\tNo tag found yet... Going up!\n")
            wait_sec = 6
            
    state_timer = Timer(wait_sec,print_state)
    state_timer.start()

def mov_drone_recorrente():
    global timer_mov_drone
    global curr_state
    global new_tag_found
    
    if drone is not None:
        
        if curr_state == "find_first_tag":
            drone.rc(0, 0, 10, 0)
            
        elif curr_state == "centralize":
            # [TODO] -> Gustavo
            if dentro_regiao():
                curr_state = "detect_qr_code"
            else:
            #    centralize() -> drone.rc(alguma direcao)
                centralizaDrone()
            # todo delete test:
            #drone.rc(0, 0, -3, 0)
            #curr_state = "detect_qr_code"
            pass
        
        elif curr_state == "detect_qr_code":
            # [TODO] -> Alguem
            # if qr_code_detected():
            #    curr_state = "process_qr_code"
            # else:
            #    detect_qr_code() -> drone.rc(alguma direcao)
            
            # todo delete test:
            curr_state = "process_qr_code"
            pass
        
        elif curr_state == "process_qr_code":
            # [TODO] -> Gabi
            # if qr_code_processed:
            #    if num_tags_detected == NUM_LIMITE_TAGS_POR_ANDAR: # Ja leu todas as tags desse andar
            #        curr_state = "goto_next_floor"
            #    else:
            #        curr_state = "goto_next_floor"
            
            # todo delete test:
            curr_state = "find_next_tag"
            pass
        
        elif curr_state == "find_next_tag":
            # [TODO] -> Marcelo: Drone deve ficar indo para direita ate achar nova Tag (considerar regiao mais a direita)
            if new_tag_found:
                curr_state = "centralize"
                new_tag_found = False
            else:
                drone.rc(7, 0, 0, 0) # FIXME: Next state should be about QR Code
                
        else:
            # Transition State, do nothing
            pass
        
    timer_mov_drone = Timer(0.1, mov_drone_recorrente) # 100 ms
    timer_mov_drone.start()

curr_dir = os.getcwd()
pics_dir = os.path.join(curr_dir, "tag-pics")
tag_counter = 0
drone_interval = 7

kill_thread = False
found_first_tag = False
new_tag_found = False

if __name__ == '__main__':

    # Color bounds
    # TODO: ajustar faixa de valores da cor azul
    # light_blue = (110, 50, 50)
    # dark_blue = (130, 255, 255)
    light_blue = (90, 50, 38)
    dark_blue = (150, 255, 255)

    # Reference Variables
    xRef = 0
    yRef = 0
    wRef = 0
    hRef = 0
    xReg = 0
    yReg = 0

    # Asserts or creates directory where tags pictures will be storage
    if not os.path.exists(pics_dir):
        os.makedirs(pics_dir)
    else:
        # TODO: Delete all files boefore a new session or just for test purposes
        delete_picture_files()


    # TODO: Ajustar valores de tolerância (depende do tamanho da nossa área azul a ser capturada, a que distância elas \
    #  serão capturadas, espaçamento entre cada quadrado azul na prateleira)
    xTol = 125
    yTol = 75

    # TODO: ajustar intervalo de tolerancia entre cada detecção
    last_detect = datetime.now()
    detection_tolerance = timedelta(seconds=0.5)
    area_limit = 6000
    isAdjusting = False

    # Drone Vars
    drone_x = 10
    last_mov = datetime.now()
    timer_drone = datetime.now()
    drone_tolerance = timedelta(seconds=3)
    drone_end = datetime.now() + timedelta(seconds=50)

    # Drone start
    drone = Tello("TELLO-C7AC08", test_mode=False)
    drone.inicia_cmds()
    sleep(drone_interval)
    drone.takeoff()
    sleep(drone_interval)
    # Set drone orientation goto(0,0,0)
#    drone.goto(0, 0, 0, 10)
#    sleep(drone_interval)
 #   drone.goto(0, 0, 35, 10)
  #  sleep(drone_interval)

    # Timers:
    timer = Timer(5,nao_morre)
    timer.start()
    timer_mov_drone = Timer(0.1, mov_drone_recorrente)
    timer_mov_drone.start()
    state_timer = Timer(1.5,print_state)
    state_timer.start()
    
    # First capture to initialize thread
    imagem = drone.current_image
    final_img = imagem.copy()
    thread = Thread(target=threaded_function, args=(5, 2,))
    thread.start()

    while True:
        imagem = drone.current_image

        imshow("Main Vison", imagem)
        imshow("Thread Vison", final_img)
        # Mostra a imagem durante 1 milissegundo e interrompe loop quando tecla q for pressionada
        if waitKey(20) & 0xFF == ord("q"):
            break

    kill_thread = True
    thread.join()
