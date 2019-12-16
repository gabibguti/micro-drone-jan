import serial
import sys
# sys.path.insert(0, '../fita_leds/')
# import app
import random
import requests
from threading import Timer


loop_func_timer = None
ARDUINO = None
package_id = 1000
url = "http://localhost:5000"
def start_leds():
  global loop_func_timer
  global ARDUINO
  # ARDUINO = serial.Serial('COM31', 9600)
  ARDUINO = serial.Serial('/dev/cu.usbmodem143101', 9600)
  loop_func_timer = Timer(0.2, loop_func)
  loop_func_timer.start()

def loop_func():
  global package_id
  texto_recebido = ARDUINO.readline().decode().strip()
  print(texto_recebido)
  if texto_recebido != "":
      args = texto_recebido.split(' ')
      if args[0] == 'novo':
          date = "2020-01-01"
          requests.get(url + "/add_package/{}/{}/{}/{}".format(package_id, date, args[1], args[2]))
          # app.add_package(str(package_id), date, args[1], args[2])
          package_id += 1
          print('novo ' + args[1] + " " +  args[2])
      elif args[0] == 'saiu':
          requests.get(url + "/remove_package/{}/{}".format(args[1], args[2]))
          # app.remove_package(args[1], args[2])
          print('saiu ' + args[1] + " " +  args[2])
  
  loop_func_timer = Timer(0.20, loop_func) # 100 ms
  loop_func_timer.start()
  

def end_leds():
  global ARDUINO
  ARDUINO.close()

# def loop_teste():
#   global ARDUINO
#   name = ""
#   while name != "exit":
#       name = raw_input("Enter command for arduino: ")
#       print (name)
#       ARDUINO.write(name)

def rainbow_leds():
  ARDUINO.write('rainbow')

def apagar_leds():
  ARDUINO.write('preto')

def novo_leds(status, numLED):
  formatted_status = ''

  if(status == 'delayed'):
    formatted_status = 'atraso'
  elif(status == 'okay'):
    formatted_status = 'emdia'

  ARDUINO.write('chegou {} {}'.format(formatted_status, numLED + 1))

def retira_leds(numLED):
  ARDUINO.write('retirar {}'.format(numLED))

def atualizar_leds(status, numLED):
  formatted_status = ''

  if(status == 'delayed'):
    formatted_status = 'atraso'
  elif(status == 'okay'):
    formatted_status = 'emdia'

  ARDUINO.write('{} {}'.format(formatted_status, numLED + 1))
  

if __name__ == '__main__':
  start_leds()