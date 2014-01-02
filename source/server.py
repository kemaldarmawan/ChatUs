import socket
import select
import sys
import thread
from SimpleXMLRPCServer import SimpleXMLRPCServer

class Server:
	def __init__(self):
		self.host = 'localhost'
		self.port = 5000
		self.backlog = 10
		self.size = 4096
		self.server = None
		self.threads = []
		self.clients = dict()

	def print_list(self):
		for c in self.threads:
			print c.username

	def open_socket(self):
		try:
			self.server = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
			self.server.setsockopt(socket.SOL_SOCKET , socket.SO_REUSEADDR , 1)
			self.server.bind((self.host,self.port))
			self.server.listen(self.backlog)
		except socket.error , (value,message):
			if self.server:
				self.server.close()
			print "Could not open socket: " + message
			sys.exit(1)

	def disconnect(self,client):
		self.threads.remove(client)
		del self.clients[client.username]
		self.broad_cast(client,"Left Chat Room")

	def send_group(self,client,msg):
		msg = "[ %s ] : " % (client.username) + msg
		for cl in self.threads:
			if cl != client:
				cl.hear(msg)

	def broad_cast(self,client,msg):
		msg = "(~SERVER~) : User %s %s" % (client.username,msg)
		print msg
		for cl in self.threads:
			if cl != client:
				cl.hear(msg)

	def run(self):
		self.open_socket()
		input  = [self.server]
		running = 1
		while running:
			inputready , outputready , exceptready = select.select(input,[],[])
			for s in inputready:
				if s == self.server:
					c = Client(self.server.accept())
					c.spoke = self.send_group
					c.disconnect = self.disconnect
					c.username = c.client.recv(4096)
					self.clients[c.username] = c
					self.threads.append(c)
					self.broad_cast(c,"Entered Chat Room")

		self.server.close()
		for c in self.threads:
			c.join()


class Client():
	def __init__(self,(client,address)):
		self.client = client
		self.address = address
		self.size = 4096
		self.username = ''
		self.spoke = None
		self.commanded = None
		self.disconnect = None
		self.speaker = thread.start_new_thread(self.__speak__,())

	def hear(self,msg):
		self.client.send(msg)

	def __speak__(self):
		running = 1
		while running:
			data = self.client.recv(self.size)
			if data:
				if data == "@disconnect":
					self.disconnect(self)
				else:
					self.spoke(self,data)
			else:
				self.client.close()
				running = 0

s = Server()
thread.start_new_thread(s.run,())

def print_user():
	return s.clients.keys()
xmlserver = SimpleXMLRPCServer(("localhost",5001))
xmlserver.register_function(print_user,"list_user")
xmlserver.serve_forever()





