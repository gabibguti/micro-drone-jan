from extra.tello import Tello
from time import sleep


def para():
    drone.land()

def mov_dronee(x, y, z, w):
    drone.goto(int(x),int(y),int(z),int(w))

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

#drone = Tello("TELLO-C7AC08", test_mode=False)
drone = Tello("TELLO-D023AE", test_mode=False)
drone.inicia_cmds()

# Set timeout drone init
sleep(5)
decola()