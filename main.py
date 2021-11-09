# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 15:34:10 2021

@author: Najmeddine
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt
import pytesseract
from scipy import ndimage
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
from pytesseract import Output
import re


# Read the image
img = cv2.imread('receipt.jpg')
# Simple thresholding
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret,thresh1 = cv2.threshold(gray,207,255,cv2.THRESH_BINARY)
cv2.imshow('gray',thresh1)
cv2.waitKey()

#image filtering 
result=ndimage.median_filter(thresh1,size=2)
cv2.imshow('gray',result)
cv2.waitKey()

fig = plt.figure()
plt.gray()  # show the filtered result in grayscale
ax1 = fig.add_subplot(121)  # left side
ax2 = fig.add_subplot(122) 
ax1.imshow(gray)
ax2.imshow(result)

# TEXT detetction
hImg, wImg= result.shape

ch = pytesseract.image_to_boxes(result,lang='deu')

for c in ch.splitlines() :
    c = c.split(" ")
    x,y,w,h = int(c[1]), int(c[2]), int(c[3]), int(c[4])
    cv2.rectangle(img, (x,hImg-y), (w, hImg-h), (0,0,255),1)
    #cv2.putText(img, c[0], ((x+w)//2,hImg-h), cv2.FONT_HERSHEY_COMPLEX, 1, (50,50,250))

cv2.imshow('gray',img)
cv2.waitKey()

#Text Recognition
extracted_text = pytesseract.image_to_string(result, lang = 'deu')
receipt_ocr = {}
splits = extracted_text.splitlines()
restaurant_name = splits[0] +" " + splits[2]

date_pattern = r'(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.](19|20)\d\d'
date = re.search(date_pattern, extracted_text).group()
receipt_ocr['date'] = date
print(date)

# get lines with chf
lines_with_chf = []
for line in splits:
  if re.search(r'CHF',line):
    lines_with_chf.append(line)

print(lines_with_chf)

# get items, total, ignore Incl
items=[]
for line in lines_with_chf:
    print(line)
    if re.search(r'Incl',line):
        continue
    if re.search(r'Tota1', line):
        total = line
    else:
        items.append(line)
      
# Get Name, quantity and cost
all_items = {}
for item in items:
    details= item.split()
    quantity_name = details[0]
    quantity = quantity_name.split('x')[0]
    name = quantity_name.split('x')[1]
    cost = details[-1]
    all_items[name] = {'quantity':quantity, 'cost':cost}
total = total.split('CHF')[-1]

# Store the results in the dict
receipt_ocr['items'] = all_items
receipt_ocr['total'] = total  

import json

receipt_json = json.dumps(receipt_ocr)
print(receipt_json)
with open('receipt_ocr', 'w') as outfile:
    json.dump(receipt_ocr, outfile)