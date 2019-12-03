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
    xDist = (xReg-xRef)*4/3
    drone.goto(int(xDist),0,0,10)

def movHoriz(xRef, xReg):
    xDist = (xReg-xRef)*4/3
    drone.goto(int(xDist),0,0,10)

def movDir(xRef, xReg):
    xDist = (xRef - xReg)*4/3
    drone.goto(int(-xDist),0,0,10)

def movBaixo(yLim, yRegLim):
    zDist = (yLim - yRegLim)*4/3
    drone.goto(0, 0, int(-zDist), 10)

def movCima(yRef, yReg):
    zDist = (yReg-yRef)*4/3
    drone.goto(0, 0, int(zDist), 10)

def movVert(yRef, yReg):
    zDist = (yReg-yRef)*4/3
    drone.goto(0, 0, int(zDist), 10)

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
# drone = Tello("TELLO-D023AE", test_mode=False)
drone.inicia_cmds()

# Set timeout drone init
# s = 7
# sleep(s)
# drone.takeoff()
# sleep(s)
# drone.rc(0,10,0,0)
# sleep(s)
# drone.rc(0,-10,0,0)
# sleep(s)
# drone.rc(0,0,0,0)
# sleep(s)
# drone.land()

s = 6
sleep(s)
drone.takeoff()
sleep(s)
drone.goto(0,0,0,10)
sleep(s)
drone.goto(60,0,0,10)
sleep(s)
# drone.rc(0,-10,0,0)
# sleep(s)
# drone.rc(0,0,0,0)
# sleep(s)
drone.land()


# while True:
    # imagem = drone.current_image
    # cv2.imshow("test", imagem)
    # if waitKey(1) & 0xFF == ord("q"):
    #         break