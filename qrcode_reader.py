# import the necessary packages
from pyzbar import pyzbar
import argparse
import cv2
import os

# load qrcode image
img_location = os.path.join('qrcode-images','IMG_QRCode_1.jpg')
image = cv2.imread(img_location)
if image is None:
  raise Exception('Error: Image not found: {}.'.format(img_location))
 
# find the barcodes in the image and decode each of the barcodes
barcodes = pyzbar.decode(image)

# loop over the detected barcodes
for barcode in barcodes:
	# extract the bounding box location of the barcode and draw the
	# bounding box surrounding the barcode on the image
	(x, y, w, h) = barcode.rect
	cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
 
	# the barcode data is a bytes object so if we want to draw it on
	# our output image we need to convert it to a string first
	barcodeData = barcode.data.decode("utf-8")
	barcodeType = barcode.type
 
	# draw the barcode data and barcode type on the image
	text = "{} ({})".format(barcodeData, barcodeType)
	cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
 
	# print the barcode type and data to the terminal
	print("[INFO]\n\nBarcode Type:\n{}\n\nBarcode data:\n{}".format(barcodeType, barcodeData))

cv2.namedWindow('Decoded QRCode', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Decoded QRCode', 600, 600)
cv2.imshow('Decoded QRCode', image)  
cv2.waitKey(0)
cv2.destroyAllWindows()
