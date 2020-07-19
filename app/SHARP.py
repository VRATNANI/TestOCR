# https://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/

# import the necessary packages
import numpy as np
import cv2
import math
from PIL import Image
import PIL.ImageOps
from imutils import contours
import imutils



def SHARP(file):
    image = cv2.imread(file)
    lower = np.array([200, 200, 200], dtype="uint8")
    upper = np.array([255, 255, 255], dtype="uint8")
	# find the colors within the specified boundaries and apply
	# the mask
    mask = cv2.inRange(image, lower, upper)
    output = cv2.bitwise_and(image, image, mask=mask)
    cv2.imwrite("frame_out.jpg", output)
    filefori = Image.open("frame_out.jpg")
    inverted_image = PIL.ImageOps.invert(filefori)
    inverted_image.save("edged.jpg")
    # define the dictionary of digit segments so we can identify
	# each digit on the thermostat
    DIGITS_LOOKUP = {
	(1, 1, 1, 0, 1, 1, 1, 0): 0,
	(1, 1, 1, 0, 1, 0, 1, 0): 0,
	(0, 0, 1, 0, 0, 1, 0, 0): 1,
	(1, 0, 1, 1, 1, 0, 1, 0): 2,
	(1, 0, 1, 1, 0, 1, 1, 0): 3,
	(0, 1, 1, 1, 0, 1, 0, 0): 4,
	(1, 1, 0, 1, 0, 1, 1, 0): 5,
	(1, 1, 0, 1, 1, 1, 1, 0): 6,
	(1, 0, 1, 0, 0, 1, 0, 0): 7,
	(1, 1, 1, 1, 1, 1, 1, 0): 8,
	(1, 1, 1, 1, 0, 1, 1, 0): 9,
	(1, 1, 1, 0, 1, 1, 1, 1): 10,
	(0, 0, 1, 0, 0, 1, 0, 1): 11,
	(1, 0, 1, 1, 1, 0, 1, 1): 21,
	(1, 0, 1, 1, 0, 1, 1, 1): 31,
	(0, 1, 1, 1, 0, 1, 0, 1): 41,
	(1, 1, 0, 1, 0, 1, 1, 1): 51,
	(1, 1, 0, 1, 1, 1, 1, 1): 61,
	(1, 0, 1, 0, 0, 1, 0, 1): 71,
	(1, 1, 1, 1, 1, 1, 1, 1): 81,
	(1, 1, 1, 1, 0, 1, 1, 1): 91,
	(0, 0, 0, 0, 0, 0, 0, 0): 99
	}
	# load the example image
    edged = cv2.imread("edged.jpg")
    gray = cv2.cvtColor(edged, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (41, 63), 0)
    thresh = cv2.threshold(
        blurred, 255, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    digitCnts = []
	# loop over the digit area candidates
    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        if (w >= 60 and w < 155) and (h >= 110 and h <= 200):
            digitCnts.append(c)
    output = edged.copy()
    box = []
    for d in digitCnts:
        box = cv2.boundingRect(d)
        (x, y, w, h) = box
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 0, 255), 3)
    
    digits = []
    coordinates=[]
    for d in digitCnts:
        coordinates.append(cv2.boundingRect(d))
    # print(coordinates)
    sortedCoord=sorted(coordinates,key=lambda x:x[0])
	# print(sortedCoord)
    ofs = 0
    deg = (11*(3.14/180))
	# loop over each of the digits
    for x, y, w, h in sortedCoord:
	# extract the digit ROI
        roi = thresh[y:y + h, x:x + w]
        ofs = int(-((0*math.cos(deg))-((h/2)*math.sin(deg))))
	# compute the width and height of each of the 7 segments
	# we are going to examine
        (roiH, roiW) = roi.shape
        (dW, dH, dHC1, dWC1) = (int(roiW * 0.25), int(roiH * 0.15), int(roiH * 0.15), int(roiW * 0.15))
        dHC = int(roiH * 0.05)
	# define the set of 7 segments
        segments = [
        ((0+ofs, 0), (w, dH)),      # top
        ((0+ofs, 0), (dW+ofs, h // 2)), # top-left
        ((w - dW-10, 0), (w-6, h // 2)),     # top-right
        ((0, (h // 2) - dHC) , (w, (h // 2) + dHC)), # center
        ((0, h // 2), (dW, h)), # bottom-left
        ((w - dW-ofs, h // 2), (w-ofs, h)),     # bottom-right
        ((0, h - dH), (w-ofs, h)),   # bottom
        ((w-dWC1, h - dHC1), (w, h))  #dot
        ]
        on = [0] * len(segments)
	# loop over the segments
        for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
	
	# extract the segment ROI, count the total number of
	# thresholded pixels in the segment, and then compute
	# the area of the segment
            segROI = roi[yA:yB, xA:xB]
            total = cv2.countNonZero(segROI)
            area = (xB - xA) * (yB - yA)
	# if the total number of non-zero pixels is greater than
	# 50% of the area, mark the segment as "on"
            if total / float(area) > 0.5:
                on[i]= 1
	# lookup the digit and draw it on the image
        digit = DIGITS_LOOKUP[tuple(on)]
        digits.append(digit)
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 1)
        cv2.putText(output, str(digit), (x - 10, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
    
    result=""
    for dig in digits:
        if(dig==99):
            continue
        elif(dig>10):
            result += str(int(dig/10))+"."
        elif(dig<=9):
            result += str(dig)
        elif (dig==10):
            result+="0."
    return (str(result))
	# print("Weight: "+result+" kgs")
	# print("Float",float(result))((
#print(SHARP("D:\\Work\\OCR-2\\MahycoWeighInt12n4\\Final_Sharp\\Mahyco\\Samples\\SHARP1-PO12345671-BAG3.jpg"))
#print(SHARP("C:\\Users\\varan\\OneDrive\\Desktop\\Test\\test.jpg"))

