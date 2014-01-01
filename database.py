import MySQLdb as mysql
import MySQLdb.cursors
import time
import os

db = mysql.Connect(host="localhost",user="root",passwd="root",db="chat",cursorclass=mysql.cursors.DictCursor)
cur = db.cursor()

def InsertUser((username,password)):
	sql = "INSERT INTO USR VALUES('%s','%s')" % (username,password)
	try:
		cur.execute(sql)
		db.commit()
		os.system("clear")
		print "You have registered!"
		print time.sleep(2)
	except:
		os.system("clear")
		print "Username already exist!"
		print time.sleep(2)
		db.rollback()

def CheckUser((username,password)):
	sql = "SELECT * FROM USR WHERE USERNAME = '%s'" % (username)
	res = cur.execute(sql)
	return res

def CheckPassword((username,password)):
	sql = "SELECT * FROM USR WHERE USERNAME = '%s' AND PASSWORD = '%s'" % (username,password)
	res = cur.execute(sql)
	return res