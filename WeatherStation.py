import MySQLdb
from time import *
#from flask import Flask
#app = Flask(__name__);



db = MySQLdb.connect(host='localhost',user='monitor',passwd='password',db='weather');
curs = db.cursor();

i = 0

def main():
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
                        values(CURRENT_DATE(),NOW(),0,0)""")
            curs.execute ("SELECT * FROM weatherdata")

            for reading in curs.fetchall():
                print str(reading[0])+"	"+str(reading[1])+" 	"+"    " + reading[2]+"  	"+str(reading[3])
            db.close();
    j=j+1
#@app.route('/')
#def index():
#    return strftime("%a, %d %b %Y %H:%M:%S",gmtime())
#
#if __name__ == '__main__':
#    app.run(debug=True,host='0.0.0.0')

main();
db.close();
