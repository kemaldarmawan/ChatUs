import os
import time
import xmlrpclib
import sys
import Tkinter
import tkFileDialog
import thread
import signal
from database import *
from menu import *
from client import ChatClient
from server import bcolors


def print_list():
	users = proxy.list_user()
	print bcolors.warning_message("~ChatUs~ :")
	for user in users:
		print bcolors.whisper_message("* %s" % user)
	print bcolors.warning_message("%s user(s) online" % (str(len(users))))
	print bcolors.warning_message("-------------------")


def filter_message(msg):
	if len(msg)>=1:
		if msg[0]=='~':
			if(msg[1:].split(' ')[0]=='quit'):
				return (-2 , 'disconnect')
			elif(msg[1:].split(' ')[0]=='file'):
				root = Tkinter.Tk()
				root.withdraw()
				file_path = ''
				try:
					file_path = tkFileDialog.askopenfilename()
				except:
					print "jir masuk"
					pass
				file_ = ''
				if file_path:
					file_name = file_path[file_path.rfind("/")+1:]
					#print file_name
					try :
						file_data = open(file_path,"r").read()
						file_ = "file\r\n"+file_name+"\r\n\r\n"+str(len(file_data))+"\r\n\r\n"+file_data+"\r\n\r\n\r\n"
					except:
						pass
				return (3,file_)
			elif msg[1:].split(' ')[0]=='whosonline':
				return (2,"user online")
			else:
				return (0,msg)
		elif msg[0]=='@':
			if len(msg)>1 and msg[1:].split(' ')[0] in proxy.list_user():
				if len(msg.split(" ")) > 1 and msg.split(" ")[1] == "~file":
					file_path = ''
					try:
						root = Tkinter.Tk()
						root.withdraw()
						file_path = tkFileDialog.askopenfilename()
					except:
						file_path = ''
					file_ = ''
					if file_path:
						file_name = file_path[file_path.rfind("/")+1:]
						file_to = msg[1:].split(" ")[0]
						#print file_name
						file_data = open(file_path,"r").read()
						file_ = "fileto\r\n"+file_to+"\r\n\r\n"+file_name+"\r\n\r\n"+str(len(file_data))+"\r\n\r\n"+file_data+"\r\n\r\n\r\n"
					return (11,file_)
				return (1,msg.split("@")[1])
			elif len(msg)>1 and msg[1:].split(' ')[0] not in proxy.list_user():
				return (-1,msg.split("@")[1])
			else: return (0,msg)
		else:
			return (0,msg)
	else:
		return (0,msg)


def signal_handler(signal,frame):
	c.disconnect()
	sys.exit(0)

def login(username):
	os.system("clear")
	c = ChatClient()

	if c.connect(username):
		sys.stdout.write("\x1b]2;%s\x07" % (c.username))
		try:

			while c.connected == 1:
				msg = raw_input()
				msg = msg.strip()
				print "\033[A                             \033[A"
				if(len(msg)==0):
					continue
				try:
					cmd , temp = filter_message(msg)
					if cmd==-2:
						c.disconnect()
						clear_screen("Disconnecting...")
						break
					elif cmd==1:
						if len(msg.split(' ')) == 1:
							print bcolors.warning_message("~ChatUs~ : ") + bcolors.whisper_message("user %s is online" % (temp))
						else:
							print bcolors.whisper_message("<You> : %s" % (msg))
							c.say(msg)
					elif cmd==11:
						c.say(temp)
						print bcolors.whisper_message("<You> : Send file to %s" % (msg))
					elif cmd==-1:
						print bcolors.warning_message("~ChatUs~ : ") + bcolors.fail_message("user %s is offline" % (temp))
					elif cmd==2:
						print_list()
					elif cmd==3:
						if temp != '':
							c.say(temp)
					else:
						if(len(msg)>=1):
							print bcolors.normal_message("<You> : %s" % (msg))
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
	c = None
	try:
		proxy = xmlrpclib.ServerProxy("http://localhost:5001/")
	except:
		pass
	try:
		signal.signal(signal.SIGHUP , signal_handler)
		while True:
			sys.stdout.write("\x1b]2;ChatUs\x07")
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
				login("guest\r\n")
			elif cmd == '4':
				break
			else:
				clear_screen("Not a valid command")

		signal.pause()
	except KeyboardInterrupt:
		clear_screen("Exiting ChatUs...")
		os.system("clear")