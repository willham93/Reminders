# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

# to get running in terminal enter
# lt --port 5000 --subdomain pymailer5547

import csv
import threading
from datetime import datetime as dt
import mariadb
import time
import sys
import ezgmail
import os


#from adafruit_servokit import ServoKit
from flask import Flask, Response, redirect, render_template, url_for
# import the necessary packages
from flask.globals import request
from flask.wrappers import Request


# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
try: conn=mariadb.connect(
    user="reminder",
    password="hami5547",
    host="127.0.0.1",
    port=3306,
    database="remindersdb")
except mariadb.Error as e:
    print(f"error connecting:{e}")
    sys.exit(1)
    
cur = conn.cursor()

cur.execute("SELECT * FROM Reminders WHERE name=?",("william",))
for x in cur:
    print(x)

lock = threading.Lock()
temp = time.time()
# initialize a flask object
app = Flask(__name__)



old_name=""
old_eAdd = ""
old_msg = ""
old_t = ""

os.chdir(r'/home/william/Desktop/HDD/pythonprojects/reminder/local_server/static')
ezgmail.init()


# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()

def readAndParseEmail():
	global lock,old_eAdd,old_msg,old_name,old_t
	unreadThreads = ezgmail.unread() # List of GmailThread objects.
	if len(unreadThreads) > 0:
 		for t in unreadThreads:
			 t.markAsRead()
			 msg = t.messages[0].body
			 contents = msg.split('\r\n')
			 name = contents[0]
			 eAdd = contents[1]
			 reminder = contents[2]
			 date = contents[3]
			 Time = contents[4]
			 query = f"INSERT INTO Reminders (name,email_address,message,date,time) VALUES (\'{name}\',\'{eAdd}\',\'{reminder}\',\'{date}\',\'{Time}\')"
			 txt = [name,eAdd,reminder,date,Time]
			 if "new reminder" in t.messages[0].subject.lower():
				 with lock:
					 if not old_t == t or not old_name == name or not old_eAdd == eAdd or not old_msg==msg:
				 		old_t = Time
				 		old_eAdd = eAdd
				 		old_msg = msg
				 		old_name = name
				 		cur.execute(query)
						





def readAndSendReminders():
	with lock:
		lines = list()
		now = dt.now()
		now=now.strftime("%Y-%m-%d %H:%M")
		t = now.split(' ')[1]
		date = now.split(' ')[0]

		cur.execute("SELECT * FROM Reminders where date=? AND time=?",
                    (now.split(' ')[0],now.split(' ')[1]))
		
		for row in cur:
			name = row[0].replace("'",'')
			reciever = row[1].replace("'",'')
			body=row[2].replace("'",'')
			subject = "Reminder for " + name
			ezgmail.send(reciever,subject,body)
			query = f"DELETE FROM Reminders WHERE name='{name}' AND email_address='{reciever}' AND message='{body}' AND date='{date}' AND time='{t}'"
			lines.append(query)
		for line in lines:
			cur.execute(line)
			conn.commit()


			


def threadFunction():
	global temp
	while(True):
		x = time.time()
		if x - temp >=1:
			readAndSendReminders()
			readAndParseEmail()
			temp = x

@app.route("/")
def index():

	# return the rendered template
	return render_template("index.html")

@app.route("/", methods=["POST"])
def addReminder():
	global old_name,old_eAdd,old_msg,old_t
	name = request.form['name'] 
	eAdd = request.form['address']
	msg = filter = request.form['reminder']
	date = request.form['Date']
	t = request.form.get("tod")
	txt = [name,eAdd,msg,date,t]
	print(txt)
	with lock:
		if not old_t == t or not old_name == name or not old_eAdd == eAdd or not old_msg==msg:
			old_t = t
			old_eAdd = eAdd
			old_msg = msg
			old_name = name
			query = f"INSERT INTO Reminders (name,email_address,message,date,time) VALUES (\'{name}\',\'{eAdd}\',\'{msg}\',\'{date}\',\'{t}\')"
			print(query)
			cur.execute(query)
			conn.commit()

	return render_template("index.html")

# check to see if this is the main thread of execution
if __name__ == '__main__':

	t = threading.Thread(target=threadFunction)
	t.daemon = True
	t.start()



	# start the flask app
	#app.run(host=args["ip"], port=args["port"], debug=True,
	#	threaded=True, use_reloader=False)

	app.run(host="127.0.0.1", port="5000", debug=True,
		threaded=True, use_reloader=False)


