import os
import time
import xmlrpclib
import sys
from database import *
from menu import *
from client import ChatClient


def filter_message(msg):
	if msg[0]=='~':
		if(msg[1:].split(' ')[0]=='quit'):
			return (-1 , 'disconnect')
	else:
		return (0,msg)

def login(username):
	os.system("clear")
	print "Welcome to ChatUs %s !" % (username)
	c = ChatClient()
	c.connect(username)
	while True:
		msg = raw_input()
		try:
			cmd , msg = filter_message(msg)
			if(cmd==-1): 
				c.disconnect()
				os.system("clear")
				print "Disconnecting..."
				time.sleep(2)
				break
			else:
				c.say(msg)
		except:
			print "Disconnected from server!"
			break


if __name__ == '__main__':
	cmd = 0
	proxy = xmlrpclib.ServerProxy("http://localhost:5001/")
	while cmd == 0:
		cmd = MenuForm()
		if cmd == '1':
			username , password = LoginForm()
			if CheckPassword((username,password)) == 1:
				if username in proxy.list_user():
					os.system("clear")
					print "Username %s already logged in" % (username)
					print time.sleep(2)
					cmd = 0
				else:
					login(username)
					cmd = 0
					
		elif cmd == '2':
			InsertUser(RegisterForm())
			cmd = 0
		elif cmd == '3':
			cmd = 0
		elif cmd == '4':
			pass
		else:
			cmd = 0
			os.system("clear")
			print "Not a valid command!"
			print time.sleep(2)
		os.system("clear")