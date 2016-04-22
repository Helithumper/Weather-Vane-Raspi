import MySQLdb
from time import *
from random import *
import threading
import smbus
import RPi.GPIO as GPIO
#import Adafruit_BMP.BMP085 as BMP085

GPIO.setmode(GPIO.BCM)
#from flask import Flask
#app = Flask(__name__);

#sensor = BMP085.BMP085(0x60, bus=SMBus(1), mode = BMP085.BMP085_STANDARD);
#sensor = BMP085.BMP085();

db = MySQLdb.connect(host='45.55.180.111',user='peyton',passwd='toor',db='weather');
curs = db.cursor();

bus = smbus.SMBus(1)
address = 0x48

SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

anemometer_pin = 0;

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(17,GPIO.OUT)

def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)

        adcout >>= 1       # first bit is 'null' so drop it
        return adcout
def getTemp():
    readout = bus.read_byte(address)
    print(readout)
    if readout>=128:
        readout=(readout-128)*-1
    cel = readout
    #cel = sensor.read_temperature();
    fah = cel*1.8+32
    return fah;

def getWindSpeed():
    anemometer = readadc(anemometer_pin, SPICLK, SPIMOSI, SPIMISO, SPICS) - 123
    speed = translate(anemometer, 0, 256, 0, 33);
    return speed;
def getPressure():
    pas = sensor.read_pressure();
    inches = pas * 0.0002953;
    return inches;
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)
def loopedFunction():
    threading.Timer(2.0, loopedFunction).start()
    GPIO.output(17,False);

    #db = MySQLdb.connect(host='45.55.180.111:3306',user='peyton',passwd='toor',db='weather');
    curs = db.cursor()

    with db:
        a = getTemp()# getTemp()
        b= getWindSpeed()
        c = 0#getPressure()
        d = 0#lightLevel()
        query = """INSERT INTO weatherdata values(CURRENT_DATE(),NOW(),{},{},{},{})""".format(a,b,c,d)
        curs.execute (query)
    curs.execute ("SELECT * FROM weatherdata ORDER BY tddate DESC,ttime DESC LIMIT 1")

    for reading in curs.fetchall():
        print str(reading[0])+"    "+str(reading[1])+"    " + str(reading[2])+"    "+str(reading[3])+"    "+str(reading[4])
    GPIO.output(17,True);

    #db.close();


#@app.route('/')
#def index():
#    return strftime("%a, %d %b %Y %H:%M:%S",gmtime())
#
#if __name__ == '__main__':
#    app.run(debug=True,host='0.0.0.0')


loopedFunction()
#db.close();
