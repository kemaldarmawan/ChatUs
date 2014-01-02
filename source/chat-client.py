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
	if c.connect(username):
		try:
			while c.connected == 1:
				msg = raw_input()
				print "\033[A                             \033[A"
				print "<You> : " + msg
				try:
					cmd , msg = filter_message(msg)
					if(cmd==-1): 
						c.disconnect()
						clear_screen("Disconnecting...")
						break
					else:
						c.say(msg)
				except:
					break
		except KeyboardInterrupt:
			c.disconnect()
			clear_screen("Disconnecting...")
	else:
		clear_screen("Server is offline")

def clear_screen(message):
	os.system("clear")
	print message
	time.sleep(2)


if __name__ == '__main__':
	try:
		proxy = xmlrpclib.ServerProxy("http://localhost:5001/")
	except:
		pass
	while True:
		cmd = MenuForm()
		if cmd == '1':
			username , password = LoginForm()
			if CheckPassword((username,password)) == 1:
				try:
					if username in proxy.list_user():
						clear_screen("Username %s already logged in" % (username))
					else:
						login(username)
				except:
					clear_screen("Server is offline")
					pass
			else:
				clear_screen("Invalid username or password")

		elif cmd == '2':
			InsertUser(RegisterForm())
		elif cmd == '3':
			pass
		elif cmd == '4':
			break
		else:
			clear_screen("Not a valid command")
		os.system("clear")