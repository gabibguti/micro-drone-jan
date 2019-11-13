from cv2 import *

def is_square(contour):
    # initialize the shape name and approximate the contour
    shape = "unidentified"
    peri = arcLength(contour, True)
    approx = approxPolyDP(contour, 0.04 * peri, True)
    # if the shape has 4 vertices, it is either a square or a rectangle
    if len(approx) == 4:
        return True
        # # compute the bounding box of the contour and use the bounding box to compute the aspect ratio
        # (x, y, w, h) = boundingRect(approx)
        # ar = w / float(h)
        # # a square will have an aspect ratio that is approximately equal to one, otherwise, the shape is a rectangle
        # shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
    return False

# Color bounds
light_blue = (110, 50, 50)
dark_blue = (130, 255, 255)

xRef = 0
yRef = 0
compRef = 0
altRef = 0


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
        print(contorno)
        x, y, comprimento, altura = boundingRect(contorno)
        if comprimento * altura > 2000 and comprimento * altura > area:
            xRef = x
            yRef = y
            compRef = comprimento
            altRef = altura
            area = comprimento * altura
    rectangle(blue_img, pt1=(xRef, yRef), pt2=(xRef + compRef, yRef + altRef), color=(0, 255, 0), thickness=3)

    imshow("Minha Janela", blue_img)

    # Take picture and save it # TODO
    # imwrite("test-pic.png", imagem)

    # Mostra a imagem durante 1 milissegundo e interrompe loop quando tecla q for pressionada
    if waitKey(1) & 0xFF == ord("q"):
        break

stream.release()
destroyAllWindows()


# from cv2 import *
# stream = VideoCapture(0)
# while True:
#     _, imagem = stream.read()
#     # Desenho de Elementos na Imagem
#     rectangle(imagem, pt1=(550,200), pt2=(850,300), color=(0,255,0), thickness=3)
#     circle(imagem, (700,400), 90, color=(255,255,0), thickness=7)
#     putText(imagem, "Jan K. S", (10,600), color=(255,255,255), thickness=4, fontFace=FONT_HERSHEY_SIMPLEX, fontScale=2)
#     imshow("Minha Janela", imagem)
#     if waitKey(1) & 0xFF == ord("q"):
#         break
#
# stream.release()
# destroyAllWindows()
#
