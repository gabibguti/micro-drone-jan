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
		[key, value] = line.split(': ')
		formattedData[key] = value

	if(render_inspection_img):
		# extract the bounding box location of the barcode and draw the
		# bounding box surrounding the barcode on the image
		(x, y, w, h) = barcode.rect
		cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
		# draw the barcode data and barcode type on the image
		text = "{} ({})".format(barcodeData, barcodeType)
		cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

		cv2.namedWindow('Decoded QRCode', cv2.WINDOW_NORMAL)
		cv2.resizeWindow('Decoded QRCode', 600, 600)
		cv2.imshow('Decoded QRCode', image)  
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	return formattedData

read_qrcode('IMG_QRCode_1.jpg')
