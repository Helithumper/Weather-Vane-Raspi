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

i = 0
def getTemp():
    readout = bus.read_byte(address)
    print(readout)
    if readout>=128:
        readout=(readout-128)*-1
    return readout
    
def main():
    print("hi")
    j=0
    print(strftime("%a, %d %b %Y %H:%M:%S",gmtime()))
    while 1:
        if j%5==0:
            db = MySQLdb.connect(host='localhost',user='monitor',passwd='password',db='weather');
            curs = db.cursor()

            print("5 Seconds have passed")
            print(strftime("%a, %d %b %Y %H:%M:%S",gmtime()))
            with db:
                curs.execute ("""INSERT INTO weatherdata
                        values(CURRENT_DATE(),NOW(),0,0,0)""")
            curs.execute ("SELECT * FROM weatherdata")

            for reading in curs.fetchall():
                print str(reading[0])+"	"+str(reading[1])+"     " + str(reading[2])+"  	"+str(reading[3])+"  	"+str(reading[4])
            db.close();
    j=j+1

def loopedFunction():
    threading.Timer(2.0, loopedFunction).start()
    j=0
    if j%5==0:
        db = MySQLdb.connect(host='localhost',user='monitor',passwd='password',db='weather');
        curs = db.cursor()

        #print("5 Seconds have passed")
        print(strftime("%a, %d %b %Y %H:%M:%S",gmtime()))
        a = getTemp()
        b = randint(0,100)
        c = randint(0,100)
        with db:
            query = """INSERT INTO weatherdata values(CURRENT_DATE(),NOW(),{},{},{})""".format(a,b,c)
            curs.execute (query)
        curs.execute ("SELECT * FROM weatherdata ORDER BY tdate DESC LIMIT 1")

        for reading in curs.fetchall():
            print str(reading[0])+"    "+str(reading[1])+"    " + str(reading[2])+"    "+str(reading[3])+"    "+str(reading[4])

        db.close();
        j=j+1
#@app.route('/')
#def index():
#    return strftime("%a, %d %b %Y %H:%M:%S",gmtime())
#
#if __name__ == '__main__':
#    app.run(debug=True,host='0.0.0.0')

loopedFunction()
db.close();
