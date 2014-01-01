from database import *
from menu import *
from classclient import ChatClient
import os
import time
import xmlrpclib


def Login(username):
	os.system("clear")
	print "Welcome to ChatUs %s !" % (username)
	c = ChatClient()
	c.connect(username)
	while True:
		msg = raw_input()
		try:
			c.say(msg)
		except:
			print "Disconnected from server!"
			sys.exit(1)




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
					Login(username)
					
		elif cmd == '2':
			InsertUser(RegisterForm())
			cmd = 0
		elif cmd == '3':
			cmd = 0
		else:
			cmd = 0
			os.system("clear")
			print "Not a valid command!"
			print time.sleep(2)
		os.system("clear")


