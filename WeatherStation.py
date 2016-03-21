import MySQLdb
from time import *
from random import *
import threading
import smbus
import RPi.GPIO as GPIO
import Adafruit_BMP.BMP085 as BMP085

GPIO.setmode(GPIO.BCM)
#from flask import Flask
#app = Flask(__name__);

sensor = BMP085.BMP085(mode = BMP085.BMP085_STANDARD);


db = MySQLdb.connect(host='localhost',user='monitor',passwd='password',db='weather');
curs = db.cursor();

bus = smbus.SMBus(1)
address = 0x48

SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

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
    #readout = bus.read_byte(address)
    #print(readout)
    #if readout>=128:
    #    readout=(readout-128)*-1
    #return readout
    cel = sensor.read_temperature();
    fah = cel*1.8+32
    return fah;

def getWindSpeed():
    return 0;
def getPressure():
    pas = sensor.read_pressure();
    inches = pas * 0.0002953;
    return inches;
def loopedFunction():
    threading.Timer(2.0, loopedFunction).start()

    db = MySQLdb.connect(host='localhost',user='monitor',passwd='password',db='weather');
    curs = db.cursor()

    with db:
        alpha = getTemp()
        b = getWindSpeed()
        c = getPressure()
        query = """INSERT INTO weatherdata values(CURRENT_DATE(),NOW(),{},{},{})""".format(getTemp(),b,c)
        curs.execute (query)
    curs.execute ("SELECT * FROM weatherdata ORDER BY tdate,ttime DESC LIMIT 1")

    for reading in curs.fetchall():
        print str(reading[0])+"    "+str(reading[1])+"    " + str(reading[2])+"    "+str(reading[3])+"    "+str(reading[4])

    db.close();


#@app.route('/')
#def index():
#    return strftime("%a, %d %b %Y %H:%M:%S",gmtime())
#
#if __name__ == '__main__':
#    app.run(debug=True,host='0.0.0.0')


loopedFunction()
db.close();
