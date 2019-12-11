from cv2 import *
from datetime import datetime, timedelta
import os
from time import sleep
from threading import Thread

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

def take_picture(img, x, xRef, y, yRef, xTol, w, h):
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

        # TODO: Decidir formato que arquivo deve ser salvo ex: '{X1}_{Y1}_{X2}_{Y2}_{DATA/HORA}.png'
        # Take picture and save it
        tag_picture = os.path.join(pics_dir, "tag" + str(tag_counter + 1) + ".png")
        if not os.path.exists(tag_picture):
            imwrite(tag_picture, img)
            tag_counter += 1


def threaded_function(arg, arg2):
    global imagem
    global final_img
    xRef = 0
    yRef = 0
    wRef = 0
    hRef = 0

    # TODO: Ajustar valores de tolerância (depende do tamanho da nossa área azul a ser capturada, a que distância elas \
    #  serão capturadas, espaçamento entre cada quadrado azul na prateleira)
    xTol = 125
    yTol = 75

    # TODO: ajustar intervalo de tolerancia entre cada detecção
    last_detect = datetime.now()
    detection_tolerance = timedelta(seconds=0.5)
    area_limit = 3000
    show_rect = False
    counter_no_rect = 0
    COUNTER_LIMIT = 250

    while True:
        # Parte 1
        imagem_hsv = cvtColor(imagem, COLOR_BGR2HSV)
        mascara = inRange(imagem_hsv, light_blue, dark_blue)
        imagem1 = bitwise_and(imagem, imagem, mask=mascara)

        # Parte 2
        graybgr = cvtColor(imagem, COLOR_BGR2GRAY)
        graybgr = cvtColor(graybgr, COLOR_GRAY2BGR)

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
                # if is_square(w, h) and w * h > area_limit:
                if w * h > area_limit:
                    show_rect = True
                    take_picture(blue_img, x, xRef, y, yRef, xTol, w, h)
                    xRef = x
                    yRef = y
                    wRef = w
                    hRef = h
                    counter_no_rect = 0
                else:
                    counter_no_rect+=1
                if counter_no_rect >= COUNTER_LIMIT:
                    show_rect = False

        if show_rect:
            rectangle(blue_img, pt1=(xRef, yRef), pt2=(xRef + wRef, yRef + hRef), color=(0, 255, 0), thickness=3)

        final_img = blue_img
        if kill_thread:
            break
    print("Thread died")


curr_dir = os.getcwd()
pics_dir = os.path.join(curr_dir, "tag-pics")
tag_counter = 0

# Old range
# light_blue = (90, 50, 38)
# dark_blue = (150, 255, 255)

# Good for pc
light_blue = (90, 150, 0)
dark_blue = (150, 255, 255)

# Good for webcam
# light_blue = (100, 150, 15)
# dark_blue = (140, 255, 255)

kill_thread = False

if __name__ == '__main__':
    # Asserts or creates directory where tags pictures will be storage
    if not os.path.exists(pics_dir):
        os.makedirs(pics_dir)
    else:
        delete_picture_files()

    stream = VideoCapture(0)

    # First capture to initialize thread
    _, imagem = stream.read()
    final_img = imagem.copy()
    thread = Thread(target=threaded_function, args=(5, 2,))
    thread.start()

    while True:
        _, imagem = stream.read()

        imshow("Minha Janela", final_img)
        # Mostra a imagem durante 1 milissegundo e interrompe loop quando tecla q for pressionada
        if waitKey(1) & 0xFF == ord("q"):
            break

    kill_thread = True
    thread.join()
    stream.release()
    destroyAllWindows()
