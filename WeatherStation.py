import MySQLdb
from time import *
from random import *
import threading
import smbus
#from flask import Flask
#app = Flask(__name__);



db = MySQLdb.connect(host='localhost',user='monitor',passwd='password',db='weather');
curs = db.cursor();

bus = smbus.SMBus(1)
address = 0x48

def getTemp():
    readout = bus.read_byte(address)
    #print(readout)
    if readout>=128:
        readout=(readout-128)*-1
    return readout

def loopedFunction():
    threading.Timer(2.0, loopedFunction).start()

    db = MySQLdb.connect(host='localhost',user='monitor',passwd='password',db='weather');
    curs = db.cursor()

    with db:
        alpha = getTemp()
        b = randint(0,100)
        c = randint(0,100)
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
