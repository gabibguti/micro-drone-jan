# import the necessary packages
from pyzbar import pyzbar
import argparse
import cv2
import os
import json

def read_qrcode(img_name, render_inspection_img = False):
	# load qrcode image
	img_location = os.path.join('qrcode-images', img_name)
	image = cv2.imread(img_location)
	if image is None:
		raise Exception('Error: Image not found: {}.'.format(img_location))
	
	# find all barcodes in the image and decode them
	barcodes = pyzbar.decode(image)
	if(len(barcodes) == 0):
		raise Exception('Error: No barcode found in image.')
	elif(len(barcodes) > 1):
		raise Exception('Error: Too many barcodes found in image.')
	barcode = barcodes[0]

	# the barcode data is a bytes object so if we want to draw it on
	# our output image we need to convert it to a string first
	barcodeData = barcode.data.decode("utf-8")
	barcodeType = barcode.type

	# print the barcode type and data to the terminal
	print("[INFO]\n\nBarcode Type:\n{}\n\nBarcode data:\n{}".format(barcodeType, barcodeData))

	# transform unicode data retrieved from barcode into dict
	formattedData = {}
	lines = barcodeData.split('\r\n')
	for line in lines:
		if(len(line) > 0):
			[key, value] = line.split(': ')
			formattedData[key] = value

	if(render_inspection_img):
		# extract the bounding box location of the barcode and draw the
		# bounding box surrounding the barcode on the image
		(x, y, w, h) = barcode.rect
		cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
		# draw the barcode data and barcode type on the image
		pos_x = 10
		pos_y = 40
		for line in lines:
			text = "{}".format(line)
			cv2.putText(image, text, (pos_x, pos_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
			pos_y += pos_y

		cv2.namedWindow('Decoded QRCode', cv2.WINDOW_NORMAL)
		cv2.resizeWindow('Decoded QRCode', 600, 600)
		cv2.imshow('Decoded QRCode', image)  
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	return formattedData

read_qrcode('DRONE_IMG_1.jpeg', True)
