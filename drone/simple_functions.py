from cv2 import *

def is_new_square(x, xRef, y, yRef, tol):
    xTol = tol
    yTol = tol
    if (x > xRef - xTol and x < xRef + xTol) and (y > yRef - yTol and y < yRef + yTol):
        return False
    return True

def is_square(w, h):
    # A square will have an aspect ratio that is approximately equal to one, otherwise, the shape is a rectangle
    ar = w / float(h)
    if ar >= 0.95 and ar <= 1.05: # Its a Square
        return True
    else: # its a Rectangle
        return False


def delete_picture_files(temp_dir):
    for tag_picture in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir,tag_picture))

def apply_mask(imagem, light_bound, dark_bound):
    imagem_hsv = cvtColor(imagem, COLOR_BGR2HSV)
    mascara = inRange(imagem_hsv, light_bound, dark_bound)
    imagem1 = bitwise_and(imagem, imagem, mask=mascara)
    graybgr = cvtColor(imagem, COLOR_BGR2GRAY)
    graybgr = cvtColor(graybgr, COLOR_GRAY2BGR)
    blue_img = addWeighted(graybgr, 1, imagem1, 1, 0)
    return blue_img, mascara
