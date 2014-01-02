from socket import *
import thread
import sys
import xmlrpclib

class ChatClient:
	def __init__(self,host='localhost',port=5000):
		self.address = host , port
		self.mxbf = 4096
		self.sock = None
		self.connected = 0

	def connect(self,username):
		try:
			self.sock = socket(AF_INET , SOCK_STREAM)
			self.sock.connect(self.address)
			self.connected = 1
			self.sock.send(username)
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
					print msg
			except:
				print "Disconnected from server"
				self.sock = None