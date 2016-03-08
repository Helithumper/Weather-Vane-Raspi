import MySQLdb
from time import *
from flask import flask
app = Flask(_name_)

@app.route('/')

db = MySQLdb.connect("localhost","monitor","password","temps")
curs = db.cursor()

secondsCursor = time.time()

def main():
    print(strftime("%a, %d %b %Y %H:%M:%S",gmtime()))
    while 1:
        if(time.time()-secondsCursor==5):
            print("5 Seconds have passed")
            print(strftime("%a, %d %b %Y %H:%M:%S",gmtime()))

def index():
    return strftime("%a, %d %b %Y %H:%M:%S",gmtime())

if _name_ == '_main_':
    app.run(debug=True,host='0.0.0.0')

main();
