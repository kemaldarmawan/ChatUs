from socket import *
import thread
import sys
import xmlrpclib
import Tkinter, tkFileDialog

class ChatClient:
	def __init__(self,host='localhost',port=5000):
		self.address = host , port
		self.mxbf = 4096
		self.sock = None
		self.connected = 0
		self.username = ''

	def connect(self,username):
		try:
			self.sock = socket(AF_INET , SOCK_STREAM)
			self.sock.connect(self.address)
			self.connected = 1
			self.sock.send(username)
			self.username = self.sock.recv(4096)
			self.listener = thread.start_new_thread(self.__listen__,())
			return 1
		except:
			return 0

	def disconnect(self):
		self.say("@disconnect")
		self.sock.close()

	def say(self,msg):
		self.sock.send(msg)

	def __listen__(self):
		while self.sock:
			try:
				msg = self.sock.recv(self.mxbf)
				if not msg:
					self.sock.close()
					self.sock = None
					self.connected = 0
				else:
					if "file\r\n" in msg:
						file_name = msg.split("\r\n")[1]
						#print file_name
						file_size =  int(msg.split("\r\n\r\n")[1])
						file_data = msg.split("\r\n\r\n")[2]
						#print file_size
						if len(file_data) < file_size:
							count = 1
							while True:
								count += 1
								_data = self.sock.recv(self.mxbf)
								file_data += _data
								if len(file_data) >= file_size:
									break
						file_data = file_data.split("\r\n\r\n\r\n")[0]
						root = Tkinter.Tk()
						root.withdraw()
						dirname = ''
						dirname = tkFileDialog.askdirectory(parent=root,initialdir="/home/",title='Please select a directory to save file')
						if dirname:
							file_ = open(dirname+"/"+file_name,"w")
							file_.write(file_data)
							file_.close()
					else:
						print msg
						pass
			except:
				print "Disconnected from server"
				self.sock = None