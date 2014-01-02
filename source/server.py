import socket
import select
import sys
import os
import thread
import time
from SimpleXMLRPCServer import SimpleXMLRPCServer


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

    @staticmethod
    def warning_message(message):
    	return bcolors.WARNING + message + bcolors.ENDC

    @staticmethod
    def whisper_message(message):
    	return bcolors.OKGREEN + message + bcolors.ENDC

    @staticmethod
    def normal_message(message):
    	return bcolors.HEADER + message + bcolors.ENDC


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
		msg = "%s : " % (client.username) + msg
		for cl in self.threads:
			if cl != client:
				cl.hear(msg)

	def broad_cast(self,client,msg):
		msg = bcolors.warning_message("(~SERVER~) : User %s %s" % (client.username,msg))
		print msg
		for cl in self.threads:
			if cl != client:
				cl.hear(msg)

	def server_message(self,msg):
		for cl in self.threads:
			cl.hear(msg)

	def close(self):
		self.server_message("Disconnected from server")
		self.server.close()
		for c in self.threads:
			c.client.close()
			del c

	def whisper(self,client,username,msg):
		msg =  bcolors.OKGREEN + "@%s : %s" % (client.username,msg) + bcolors.ENDC
		self.clients[username].hear(msg)

	def run(self):
		os.system("clear")
		print "Server ChatUs starting..."
		time.sleep(2)
		print "Server ChatUs running..."
		self.open_socket()
		input  = [self.server]
		running = 1
		try:
			while running:
				inputready , outputready , exceptready = select.select(input,[],[])
				for s in inputready:
					if s == self.server:
						c = Client(self.server.accept())
						c.spoke = self.send_group
						c.disconnect = self.disconnect
						c.wisp = self.whisper
						c.username = c.client.recv(4096)
						self.clients[c.username] = c
						self.threads.append(c)
						self.broad_cast(c,"Entered Chat Room")
		except KeyboardInterrupt:
			server_message("\nDisconnected from server...")
			self.server.close()
			for c in self.threads:
				c.client.close()
				c.join()


class Client():
	def __init__(self,(client,address)):
		self.client = client
		self.address = address
		self.size = 4096
		self.username = ''
		self.spoke = None
		self.wisp = None
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
				elif "@" in data[0]:
					data = data[1:]
					self.wisp(self,data.split(' ')[0],data[data.find(" ")+1:])
				else:
					self.spoke(self,data)
			else:
				self.client.close()
				running = 0


if __name__ == '__main__':
	s = Server()
	try:
		thread.start_new_thread(s.run,())
	except KeyboardInterrupt:
		print "ulala"
	def print_user():
		return s.clients.keys()
	xmlserver = SimpleXMLRPCServer(("localhost",5001),logRequests=False)
	xmlserver.register_function(print_user,"list_user")
	try:
		xmlserver.serve_forever()
	except KeyboardInterrupt:
		print "\nServer ChatUs stopped..."
		time.sleep(2)
		s.close()