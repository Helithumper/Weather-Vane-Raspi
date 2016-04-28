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

ane_pin = 0;

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(17,GPIO.OUT)

ADDR = 0x60
CTRL_REG1 = 0x26
PT_DATA_CFG = 0x13

who_am_i = bus.read_byte_data(ADDR, 0x0C)
print hex(who_am_i)
if who_am_i != 0xc4:
    print "Device not active."
    exit(1)

setting = bus.read_byte_data(ADDR, CTRL_REG1)
newSetting = setting | 0x38
bus.write_byte_data(ADDR, CTRL_REG1, newSetting)

# Enable event flags
bus.write_byte_data(ADDR, PT_DATA_CFG, 0x07)

# Toggel One Shot
setting = bus.read_byte_data(ADDR, CTRL_REG1)
if (setting & 0x02) == 0:
    bus.write_byte_data(ADDR, CTRL_REG1, (setting | 0x02))


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
    anemometer = readadc(ane_pin, SPICLK, SPIMOSI, SPIMISO, SPICS) - 123
    anemometer=abs(anemometer);
    speed = translate(anemometer, 0, 256, 0, 33);
    return speed;
def getPressure():
    #status = bus.read_byte_data(ADDR,0x00)
    #while (status & 0x08) == 0:
        #print bin(status)
        #status = bus.read_byte_data(ADDR,0x00)

    p_data = bus.read_i2c_block_data(ADDR,0x01,3)
    t_data = bus.read_i2c_block_data(ADDR,0x04,2)
    status = bus.read_byte_data(ADDR,0x00)


    p_msb = p_data[0]
    p_csb = p_data[1]
    p_lsb = p_data[2]


    pressure = (p_msb << 10) | (p_csb << 2) | (p_lsb >> 6)
    p_decimal = ((p_lsb & 0x30) >> 4)/4.0



    #print "Pressure and Temperature at "+time.strftime('%m/%d/%Y %H:%M:%S%z')
    return str(pressure+p_decimal);
    #print str(celsius)+deg+"C"
    #print str(fahrenheit)+deg+"F"
def getLightSensor():
    adc_value = abs(readadc(1, SPICLK, SPIMOSI, SPIMISO, SPICS))
    Percent = translate(adc_value, 0, 1024, 0, 100)
    print("PERCENT:", Percent)
    return Percent;
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
        b= getWindSpeed();
        c = getLightSensor();
        d = getPressure();
        query = """INSERT INTO weatherdata (tdate,ttime,temp,windspeed,sunlight) values(CURRENT_DATE(),NOW(),{},{},{})""".format(a,b,c)
        curs.execute (query)
    curs.execute ("SELECT * FROM weatherdata ORDER BY tdate DESC,ttime DESC LIMIT 1")

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
