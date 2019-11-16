from cv2 import *
from datetime import datetime, timedelta

def is_square(w, h):
    # A square will have an aspect ratio that is approximately equal to one, otherwise, the shape is a rectangle
    ar = w / float(h)
    if ar >= 0.95 and ar <= 1.05: # Its a Square
        return True
    else: # its a Rectangle
        return False

# Color bounds
# TODO: ajustar faixa de valores da cor azul
# light_blue = (110, 50, 50)
# dark_blue = (130, 255, 255)
light_blue = (90, 50, 38)
dark_blue = (150, 255, 255)

# Variaveis Globais
xRef = 0
yRef = 0
wRef = 0
hRef = 0

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
            if is_square(w,h) and w*h > area_limit and w*h > area:

                # TODO-TODO: Tirar foto se posições das referencias tiverem sido alteradas e caso tenha passado x segundos:
                # if xRef != x and yRef != y:
                    # Take picture and save it
                    # imwrite("test-pic.png", imagem)

                xRef = x
                yRef = y
                wRef = w
                hRef = h
                area = w*h
                print("\n\t\t\t\t SQUARE")
                print("[REF] x:{}, y:{}, h:{}, l:{}, area:{}\n".format(xRef, yRef, wRef, hRef, area))
                last_detect = datetime.now() + detection_tolerance

    if last_detect > datetime.now():
        rectangle(blue_img, pt1=(xRef, yRef), pt2=(xRef + wRef, yRef + hRef), color=(0, 255, 0), thickness=3)
    imshow("Minha Janela", blue_img)

    # Mostra a imagem durante 1 milissegundo e interrompe loop quando tecla q for pressionada
    if waitKey(1) & 0xFF == ord("q"):
        break

stream.release()
destroyAllWindows()
