from extra.tello import Tello
from time import sleep
from cv2 import *


def para():
    drone.land()

def mov_dronee(x, y, z, w):
    drone.goto(int(x),int(y),int(z),int(w))

def dentroRegiao(img, xRef, yRef, wRef, hRef):
    wReg = int(img.shape[0]*2/3)
    xReg = int(img.shape[0]/6)
    hReg = int(img.shape[1]*2/3)
    yReg = int(img.shape[1]/6)

    areaRef = wRef * hRef
    #print("[REG] x:{}, y:{}, h:{}, l:{}, area:{}\n".format(xReg, yReg, wReg, hReg, areaRef))
    if (xReg < xRef) and (yReg < yRef):
        if (xReg + wReg) > (xRef + wRef):
            if (yReg + hReg) > (yRef + hRef):
                return True
    return False

def movEsq(xRef, xReg):
    while xReg > xRef:
        drone.rc(10, 0, 0, 0)
    drone.rc(0, 0, 0, 0)

def movDir(xLim, xRegLim):
    while xLim > xRegLim:
        drone.rc(-10, 0, 0, 0)
    drone.rc(0, 0, 0, 0)

def movCima(yLim, yRegLim):
    while yLim > yRegLim:
        drone.rc(0, 0, 10, 0)
    drone.rc(0, 0, 0, 0)

def movBaixo(yRef, yReg):
    while yRef > yReg:
        drone.rc(0, 0, -10, 0)
    drone.rc(0, 0, 0, 0)

def decola():
    a=7
    drone.takeoff()
    
    sleep(a)
    mov_dronee(0,-30,0,100)#direita olhando de tras
             
    sleep(a)
    mov_dronee(0,0,-20,100) #desce

    sleep(a)
    mov_dronee(0,30,0,100) #esquerda
    sleep(a)
    print("[INFO] Drone pronto")
    
    drone.land() #pousa



drone = Tello("TELLO-C7AC08", test_mode=False)
#drone = Tello("TELLO-D023AE", test_mode=False)
drone.inicia_cmds()

# Set timeout drone init
sleep(5)
#decola()

while True:
    imagem = drone.current_image
    cv2.imshow("test", imagem)
    if waitKey(1) & 0xFF == ord("q"):
            break