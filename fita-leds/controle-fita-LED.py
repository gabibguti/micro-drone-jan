import serial
 
ser = serial.Serial('/dev/cu.usbmodem144101', 9600)

name = ""

while name != "exit":
    name = raw_input("Enter command for arduino: ")
    print (name)
    ser.write(name)

ser.close()