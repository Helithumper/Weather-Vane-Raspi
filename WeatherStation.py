import MySQLdb
from time import *
from flask import flask
app = Flask(_name_)

@app.route('/')

db = MySQLdb.connect("localhost","monitor","password","weather")
curs = db.cursor()

secondsCursor = time.time()

def main():
    print(strftime("%a, %d %b %Y %H:%M:%S",gmtime()))
    while 1:
        if(time.time()-secondsCursor==20):
            db = MySQLdb.connect("localhost","monitor","password","temps")
            curs = db.cursor()

            print("5 Seconds have passed")
            print(strftime("%a, %d %b %Y %H:%M:%S",gmtime()))
            with db:
                curs.execute ("""INSERT INTO weather
                        values(CURRENT_DATE(),NOW(),0,0)""")
            curs.execute ("SELECT * FROM weather")

            for reading in curs.fetchall():
                print str(reading[0])+"	"+str(reading[1])+" 	"+"    " + reading[2]+"  	"+str(reading[3])
            db.close();
def index():
    return strftime("%a, %d %b %Y %H:%M:%S",gmtime())

if _name_ == '_main_':
    app.run(debug=True,host='0.0.0.0')

main();
db.close();
