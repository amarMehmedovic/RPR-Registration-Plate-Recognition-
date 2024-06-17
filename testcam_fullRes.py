import cv2
import numpy as np
import easyocr


img=cv2.imread('plate.png')

blurred = cv2.GaussianBlur(img, (5, 5), 0)
cv2.imshow('PLATE',blurred)
cv2.waitKey(0)

reader = easyocr.Reader(['en'])
result = reader.readtext(blurred)
extracted_text = ' '.join([text[1] for text in result])
print("Extracted Text:", extracted_text)