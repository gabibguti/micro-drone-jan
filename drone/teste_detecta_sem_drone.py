from cv2 import *
from datetime import datetime, timedelta
import os
# from mov_drone import *
from extra.tello import Tello
from time import sleep
from threading import Timer

# def para():
#     drone.land()
#
# def mov_dronee(x, y, z, w):
#     drone.goto(int(x), int(y), int(z), int(w))


def dentroRegiao(img, xRef, yRef, wRef, hRef):
    wReg = int(img.shape[0] * 2 / 3)
    xReg = int(img.shape[0] / 6)
    hReg = int(img.shape[1] * 2 / 3)
    yReg = int(img.shape[1] / 6)

    areaRef = wRef * hRef
    # print("[REG] x:{}, y:{}, h:{}, l:{}, area:{}\n".format(xReg, yReg, wReg, hReg, areaRef))
    if (xReg < xRef) and (yReg < yRef):
        if (xReg + wReg) > (xRef + wRef):
            if (yReg + hReg) > (yRef + hRef):
                return True
    return False

#
# def movEsq(xRef, xReg):
#     while xReg > xRef:
#         drone.rc(10, 0, 0, 0)
#     drone.rc(0, 0, 0, 0)
#
#
# def movDir(xLim, xRegLim):
#     while xLim > xRegLim:
#         drone.rc(-10, 0, 0, 0)
#     drone.rc(0, 0, 0, 0)
#
#
# def movCima(yLim, yRegLim):
#     while yLim > yRegLim:
#         drone.rc(0, 0, 10, 0)
#     drone.rc(0, 0, 0, 0)
#
#
# def movBaixo(yRef, yReg):
#     while yRef > yReg:
#         drone.rc(0, 0, -10, 0)
#     drone.rc(0, 0, 0, 0)
#
#
# def decola():
#     a = 7
#     drone.takeoff()

    # sleep(a)
    #mov_dronee(0, -30, 0, 100)  # direita olhando de tras
    # drone.rc(10, 0, 0, 0)
    # sleep(a)
    #mov_dronee(0, 0, -20, 100)  # desce

    #sleep(a)
    #mov_dronee(0, 30, 0, 100)  # esquerda
    #sleep(a)
    #print("[INFO] Drone pronto")

    # drone.land()  # pousa


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

def take_picture(x, xRef, y, yRef, xTol):
    global tag_counter

    # FIXME: Por enquanto, basta obter novos valores para as posições X e Y diferentes dos últimos \
    #  valores de Referência, para capturar uma nova foto, talvez pudessemos otimizar isso \
    #  utilizando uma contagem de tempo desde de a última vez que uma foto foi tirada
    if is_new_square(x, xRef, y, yRef, xTol):
        # drone.rc(0, 0, 0, 0)
        print("\n\tTaking Picture! (At: {})".format(datetime.now()))
        print("\t[NEW] x:{}, y:{}, h:{}, l:{}, area:{}".format(x, y, w, h, w * h))
        print("\t[IMG] tam_x:{}, tam_y:{}, img:{}".format(imagem.shape[1], imagem.shape[0], imagem.shape))
        print("\n\t\t\t[COUNTER] ", tag_counter)
        # Checks if Drone is too high or too low
        # if imagem.shape[0]/2

        # TODO: Decidir formato que arquivo deve ser salvo ex: '{X1}_{Y1}_{X2}_{Y2}_{DATA/HORA}.png'
        # Take picture and save it
        tag_picture = os.path.join(pics_dir, "tag" + str(tag_counter + 1) + ".png")
        if not os.path.exists(tag_picture):
            imwrite(tag_picture, imagem)
            tag_counter += 1

curr_dir = os.getcwd()
pics_dir = os.path.join(curr_dir, "tag-pics")
tag_counter = 0

if __name__ == '__main__':

    # Color bounds
    # TODO: ajustar faixa de valores da cor azul
    # light_blue = (110, 50, 50)
    # dark_blue = (130, 255, 255)
    light_blue = (90, 50, 38)
    dark_blue = (150, 255, 255)

    # orange
    # light_blue = (0, 60, 60)
    # dark_blue = (7, 255, 255)


    # Reference Variables
    xRef = 0
    yRef = 0
    wRef = 0
    hRef = 0

    # Asserts or creates directory where tags pictures will be storage
    if not os.path.exists(pics_dir):
        os.makedirs(pics_dir)
    else:
        # TODO: Delete all files boefore a new session or just for test purposes
        delete_picture_files()


    # TODO: Decidir se há necessidade de capturar mais de uma tag por vez
    # List used to keep last N captured squares
    # tags_lst = list()

    # TODO: Ajustar valores de tolerância (depende do tamanho da nossa área azul a ser capturada, a que distância elas \
    #  serão capturadas, espaçamento entre cada quadrado azul na prateleira)
    xTol = 125
    yTol = 75

    # TODO: ajustar intervalo de tolerancia entre cada detecção
    last_detect = datetime.now()
    detection_tolerance = timedelta(seconds=5)
    area_limit = 1500

    # Drone Vars
    drone_x = 10
    last_mov = datetime.now()
    timer_drone = datetime.now()
    drone_tolerance = timedelta(seconds=3)
    drone_end = datetime.now() + timedelta(seconds=60)

    # drone = Tello("TELLO-C7AC08", test_mode=False)
    # drone = Tello("TELLO-D023AE", test_mode=False)
    # drone.inicia_cmds()
    # Set timeout drone init
    sleep(5)
    # decola()
    first = True

    stream = VideoCapture(0)

    while True:
        _, imagem = stream.read()

        # if last_mov > datetime.now() or first:
        #     drone.rc(drone_x,0,0,0)
        #     drone_x = -drone_x
        #     last_mov = datetime.now() + drone_tolerance  # starts timer
        #     first = False
        #     if last_mov > drone_end: #finish
        #         drone.land()
        #         break

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
        for contorno in contornos:
            peri = arcLength(contorno, True)
            approx = approxPolyDP(contorno, 0.04 * peri, True)
            # if the shape has 4 vertices, it is either a square or a rectangle
            if len(approx) == 4:
                # compute the bounding box of the contour and use the bounding box to compute the aspect ratio
                (x, y, w, h) = boundingRect(approx)
                # TODO: Ajustar valor de "area_limit"
                if is_square(w, h) and w*h > area_limit and w*h > area:
                    take_picture(x, xRef, y, yRef, xTol)
                    xRef = x
                    yRef = y
                    wRef = w
                    hRef = h
                    area = w*h
                    # print("\n\t\t\t\t SQUARE")
                    # print("\t[REF] x:{}, y:{}, h:{}, l:{}, area:{}\n".format(xRef, yRef, wRef, hRef, area))
                    last_detect = datetime.now() + detection_tolerance # starts timer

        if last_detect > datetime.now():
            rectangle(blue_img, pt1=(xRef, yRef), pt2=(xRef + wRef, yRef + hRef), color=(0, 255, 0), thickness=3)
        imshow("Minha Janela", blue_img)

        # Mostra a imagem durante 1 milissegundo e interrompe loop quando tecla q for pressionada
        if waitKey(1) & 0xFF == ord("q"):
            break

    # stream.release()
    # destroyAllWindows()
