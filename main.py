import cv2
import numpy as np
import easyocr
import imutils
import mysql.connector
import time
from picamera2 import Picamera2, Preview
from libcamera import Transform
import re
from displej import lcd_init, lcd_string, LCD_LINE_1, LCD_LINE_2 ,lcd_clear
from senzor import measure_distance, cleanup

picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(transform=Transform(vflip=True, hflip=True))
capture_config = picam2.create_still_configuration(main={"size": (640, 480)}, transform=Transform(vflip=True, hflip=True))
reader = easyocr.Reader(['en'])

def piCameraConf():
    picam2.configure(preview_config)
    picam2.start()
    time.sleep(5)

def databaseConnect():
    mydb = mysql.connector.connect(
        host="localhost",
        user="rampa",
        passwd="1234"
    )
    mycursor = mydb.cursor()
    mycursor.execute("USE db")
    return mycursor, mydb

def imageProcessing(image):
    blurred = cv2.bilateralFilter(image, 13, 18, 18)
    edges = cv2.Canny(blurred, 30, 200)
    return edges


def detect_license_plate():
    mycursor, mydb = databaseConnect()
    cropped_images = []
    img = cv2.imread("passat.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = imageProcessing(img)
    #cv2.imshow('edge', edges)
    #cv2.waitKey(0)

    contours = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.018 * peri, True)
        if 4 <= len(approx) <= 9:
            cv2.drawContours(img, [approx], -1, (0, 255, 0), 2)
            x, y, w, h = cv2.boundingRect(approx)
            cropped_image = gray[y:y+h, x:x+w]
            cropped_image = cv2.bilateralFilter(cropped_image, 13, 18, 18)
            result = reader.readtext(cropped_image)
            extracted_text = ' '.join([text[1] for text in result]).upper()
            extracted_text = re.sub("[^A-Za-z0-9]", "", extracted_text)
            cv2.imshow('edge', cropped_image)
            cv2.waitKey(0)
            print(extracted_text)
            
            lcd_clear()  # Izbrisi sadrzaj displeja pre postavljanja novih poruka
            
            lcd_string("Reg broj:"+extracted_text, LCD_LINE_1)

            if extracted_text and len(extracted_text) in [7, 8]:
                cropped_images.append(cropped_image)
                
                # Proveri da li je tablica u bazi
                mycursor.execute("SELECT reg_broj FROM uposlenici")
                resultBP = mycursor.fetchall()
                access_granted = False
                for row in resultBP:
                    if row == (extracted_text,):
                        print("OTVORI RAMPU")
                        lcd_string("OTVORI RAMPU", LCD_LINE_2)
                        access_granted = True
                        break
                
                if not access_granted:
                    lcd_string("ZABRANJEN PROLAZ", LCD_LINE_2)

                mycursor.close()
                mydb.close()
                time.sleep(3)
                lcd_clear()  # Izbrisi sadrzaj displeja pre nastavka
                
                return  # Izlaz iz funkcije ako je tablica registrovana

    # Ako nema detektovane tablice
    lcd_clear()  # Izbrisi sadrzaj displeja ako nema tablice
    time.sleep(5)
    mycursor.close()
    mydb.close()


    

lcd_init()

try:
    while True:
        consistent_distance_count = 0
        while consistent_distance_count < 10:  # 3 sekunde * 10 merenja u sekundi
            distance = measure_distance()
            print(f"Proveravanje udaljenosti: {distance:.1f} cm")
            if 10 <= distance <= 40:
                consistent_distance_count += 1
            else:
                consistent_distance_count = 0
            time.sleep(0.5)
        print("Detekcija tablice po?inje...")
        detect_license_plate()
        time.sleep(3)  # Pauza pre nego ?to se ponovo proveri udaljenost
except KeyboardInterrupt:
    pass
finally:
    cleanup()
    
