from socket import *
import thread
import sys
import xmlrpclib

class ChatClient:
	def __init__(self,host='localhost',port=5000):
		self.address = host , port
		self.mxbf = 4096
		self.sock = None

	def connect(self,username):
		self.sock = socket(AF_INET , SOCK_STREAM)
		self.sock.connect(self.address)
		self.sock.send(username)
		self.listener = thread.start_new_thread(self.__listen__,())

	def disconnect(self):
		self.say("@disconnect")
		self.sock.close()

	def say(self,msg):
		self.sock.send(msg)

	def __listen__(self):
		while self.sock:
			try:
				print self.sock.recv(self.mxbf)
			except:
				print "Disconnected from server"
				self.sock = None