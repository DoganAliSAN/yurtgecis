from rpi_lcd import LCD
from box_rfid import rfid
import RPi.GPIO as GPIO
import time
from datetime import timedelta
import datetime
import fcntl
import requests,json
from unidecode import unidecode

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.OUT)

lcd = LCD()

rfid_reader = rfid("/dev/input/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.1:1.0-event-kbd")
while True:
    rfid_data = rfid_reader.read()
    print(rfid_data)

    # Get current time and calculate future time
    current_time = datetime.datetime.now()
    future_time = current_time + timedelta(seconds=10)

    # Write RFID data and time to file
    with open("id.txt", "w") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            # Write data to the file
            f.write(f"{rfid_data}|||{future_time}\n")
        finally:
            # Release the lock
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    rfid_data = rfid_data.lstrip('0')
    req_student = requests.get(f"http://127.0.0.0:5008/student/{str(rfid_data)}")
    if "error" not in req_student.json():
        check_time = str(datetime.datetime.now() - timedelta(seconds=15)) if req_student.json()[0].get("check_time")  == None else req_student.json()[0].get("check_time") 
        if datetime.datetime.now() >= datetime.datetime.strptime(check_time,"%Y-%m-%d %H:%M:%S.%f"):
            GPIO.output(17, 1)
            req = requests.get(f"http://127.0.0.0:5008/add_student/{str(rfid_data)}/{str(future_time)}")
            req = requests.get(f"http://127.0.0.0:5008/toggle_student/{rfid_data}")

            if bool(req_student.json()[0].get("status")) == False:
                lcd.text("HOSGELDINIZ",1)
            else:
                lcd.text("IYI GUNLER",1)
            lcd.text(unidecode(req_student.json()[0].get("adi_soyadi")),2)
            time.sleep(3)
            GPIO.output(17, 0)
            lcd.clear()
        else:
            GPIO.output(17, 0)
            lcd.text("Lutfen 10 saniye",1)
            lcd.text("Bekleyiniz",2)
    else:
        lcd.text("Lutfen Tekrar Basin",1)
        time.sleep(3)
        lcd.clear()