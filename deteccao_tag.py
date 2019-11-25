from cv2 import *
from datetime import datetime, timedelta
import os

def is_square(w, h):
    # A square will have an aspect ratio that is approximately equal to one, otherwise, the shape is a rectangle
    ar = w / float(h)
    if ar >= 0.95 and ar <= 1.05: # Its a Square
        return True
    else: # its a Rectangle
        return False

def is_new_square(x, y):
    if (x > xRef - xTol and x < xRef + xTol) and (y > yRef - yTol and y < yRef + yTol):
        return False
    return True

def delete_picture_files():
    for tag_picture in os.listdir(pics_dir):
        os.remove(os.path.join(pics_dir,tag_picture))

curr_dir = os.getcwd()
pics_dir = os.path.join(curr_dir, "tag-pics")

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

    tag_counter = 0

    # Asserts or creates directory where tags pictures will be storage
    if not os.path.exists(pics_dir):
        os.makedirs(pics_dir)
    # else:
        ## TODO: Delete all files boefore a new session or just for test purposes
        # delete_picture_files()


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
    area_limit = 6000

    stream = VideoCapture(0)

    while True:
        _, imagem = stream.read()

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
        image, contornos, hierarchy = findContours(mascara, RETR_TREE, CHAIN_APPROX_SIMPLE)
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

                    # FIXME: Por enquanto, basta obter novos valores para as posições X e Y diferentes dos últimos \
                    #  valores de Referência, para capturar uma nova foto, talvez pudessemos otimizar isso \
                    #  utilizando uma contagem de tempo desde de a última vez que uma foto foi tirada
                    if is_new_square(x, y):
                        print("\n\tTaking Picture! (At: {})".format(datetime.now()))
                        print("\t[NEW] x:{}, y:{}, h:{}, l:{}, area:{}".format(x, y, w, h, w*h))

                        # TODO: Decidir formato que arquivo deve ser salvo ex: '{X1}_{Y1}_{X2}_{Y2}_{DATA/HORA}.png'
                        # Take picture and save it
                        tag_picture = os.path.join(pics_dir, "tag" + str(tag_counter+1) + ".png")
                        if not os.path.exists(tag_picture):
                            imwrite(tag_picture, imagem)
                            tag_counter += 1

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

    stream.release()
    destroyAllWindows()
