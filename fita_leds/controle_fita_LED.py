import serial

ARDUINO = None

def start_leds():
  global ARDUINO
  ARDUINO = serial.Serial('/dev/cu.usbmodem144101', 9600)

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