import cv2
import easyocr
from PIL import Image
import numpy as np
from datetime import datetime
import os
import sqlite3
import uuid

harcascade = "model/haarcascade_russian_plate_number.xml"

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# DB
db_file = 'license_plates.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS license_plates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    image_path TEXT,
    license_plate_text TEXT
)
''')
conn.commit()

cap = cv2.VideoCapture(0)

cap.set(3, 640) # width
cap.set(4, 480) #height

min_area = 500
count = 0

# OCR function
def extract_license_plate_text(image_path):
    try:
        img = Image.open(image_path).convert('RGB')
        result = reader.readtext(np.array(img), detail=0)
        return " ".join(result) if result else None
    except Exception as e:
        print(f"Error during OCR extraction for {image_path}")
        return None

while True:
    success, img = cap.read()

    plate_cascade = cv2.CascadeClassifier(harcascade)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

    for (x,y,w,h) in plates:
        area = w * h

        if area > min_area:
            cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
            cv2.putText(img, "Number Plate", (x,y-5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

            img_roi = img[y: y+h, x:x+w]
            cv2.imshow("ROI", img_roi)


    
    cv2.imshow("Result", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        image_path = "plates/" + str(uuid.uuid4()) + ".jpg"
        cv2.imwrite(image_path, img_roi)
        cv2.rectangle(img, (0,200), (640,300), (0,255,0), cv2.FILLED)
        cv2.putText(img, "Plate Saved", (150, 265), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255), 2)
        cv2.imshow("Results",img)
        cv2.waitKey(500)
        # Save the text in DB
        license_text = extract_license_plate_text(image_path)
        # Store in DB
        cursor.execute('''
            INSERT INTO license_plates (timestamp, image_path, license_plate_text)
            VALUES (?, ?, ?)
        ''', (timestamp, image_path, license_text))
        conn.commit()
        count += 1
