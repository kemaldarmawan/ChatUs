import socket
import select
import sys
import os
import thread
import time
import signal
from SimpleXMLRPCServer import SimpleXMLRPCServer

"""Make text in terminal colored """
class bcolors:
    HEADER = '\033[96m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    GUEST = '\033[90m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


    @staticmethod
    def warning_message(message):
    	return bcolors.WARNING + message + bcolors.ENDC

    @staticmethod
    def whisper_message(message):
    	return bcolors.OKGREEN + message + bcolors.ENDC

    @staticmethod
    def normal_message(message):
    	return bcolors.HEADER + message + bcolors.ENDC

    @staticmethod
    def fail_message(message):
    	return bcolors.FAIL + message + bcolors.ENDC

    @staticmethod
    def guest_message(message):
    	return bcolors.GUEST + message + bcolors.ENDC

    @staticmethod
    def user_message(message):
    	return bcolors.OKBLUE + message + bcolors.ENDC

class Server:
	def __init__(self):
		self.host = 'localhost'
		self.port = 5000
		self.backlog = 10
		self.size = 4096
		self.server = None
		self.threads = []
		self.clients = dict()
		self.guest_number = 0

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
		self.broad_cast(client,bcolors.fail_message("User %s Left Chat Room" % (client.username)))

	def send_group(self,client,msg):
		username = bcolors.user_message(client.username)
		if client.isguest == 1:
			username = bcolors.guest_message(client.username)
		msg = "%s : " % (username) + msg
		for cl in self.threads:
			if cl != client:
				cl.hear(msg)

	def broad_cast(self,client,msg):
		msg = bcolors.warning_message("~ChatUs~ : ") + msg
		print msg
		for cl in self.threads:
			if cl != client:
				cl.hear(msg)

	def server_message(self,username="",msg=""):
		msg = bcolors.warning_message("~ChatUs~ : ") + msg
		if username=="":
			for cl in self.threads:
				cl.hear(msg)
		else:
			self.clients[username].hear(msg)


	def close(self):
		self.server_message(msg=bcolors.fail_message("Disconnected from server"))
		self.server.close()
		for c in self.threads:
			c.client.close()
			del c

	def whisper(self,client,username,msg):
		if client.isguest == 1:
			self.server_message(client.username,bcolors.fail_message("You must login to do whisper chat !"))
		elif self.clients[username].isguest == 1:
			self.server_message(client.username, bcolors.fail_message("Cannot whisper message to Guest"))
		elif client.username == username:
			msg = bcolors.fail_message("Cannot send message to yourself")
			self.server_message(username,msg)
		else:
			msg =  bcolors.whisper_message("@%s : %s" % (client.username,msg))
			self.clients[username].hear(msg)

	def get_guest_username(self):
		self.guest_number += 1
		return "Guest" + str(self.guest_number)

	def send_file(self,client,data):
		if client.isguest == 1:
			self.server_message(client.username,bcolors.fail_message("You must login to send a file !"))
		else:
			self.send_group(client,"Send a file")
			for cl in self.threads:
				if cl != client:
					cl.hear(data)

	def send_file_to(self,client,data):
		if client.isguest == 1:
			self.server_message(client.username,bcolors.fail_message("You must login to send a file !"))
		else:
			username = data.split("\r\n")[1].split("\r\n\r\n")[0]
			#print username
			data = data.replace("fileto","file")
			data = data.replace(username+"\r\n\r\n","")
			#print data[:20]
			self.whisper(client,username,"Send a file")
			self.clients[username].hear(data)


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
						c.sendfile = self.send_file
						c.sendfileto = self.send_file_to
						temp = c.client.recv(4096)
						if temp == "guest\r\n":
							temp = self.get_guest_username()
							c.isguest = 1
						c.username = temp
						c.hear(temp)
						self.clients[c.username] = c
						self.threads.append(c)
						if c.isguest == 0:
							self.broad_cast(c,bcolors.whisper_message("User %s Entered Chat Room" % (c.username)))
						else:
							self.broad_cast(c,bcolors.whisper_message("Guest %s Entered Chat Room" % (c.username)))
						self.server_message(username=temp,msg=bcolors.warning_message("Welcome to ChatUs %s !" % (temp)))
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
		self.sendfile = None
		self.isguest = 0
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
				elif "file\r\n" in data:
					file_data = data
					if "\r\n\r\n\r\n" not in file_data:
						while True:
							_data = self.client.recv(self.size)
							file_data += _data
							if "\r\n\r\n\r\n" in _data:
								break
					self.sendfile(self,file_data)
				elif "fileto\r\n" in data:
					file_data = data
					if "\r\n\r\n\r\n" not in file_data:
						while True:
							_data = self.client.recv(self.size)
							file_data += _data
							if "\r\n\r\n\r\n" in _data:
								break
					self.sendfileto(self,file_data)
				else:
					self.spoke(self,data)
			else:
				self.disconnect(self)
				self.client.close()
				running = 0





if __name__ == '__main__':
	s = Server()
	""" To change title in terminal """
	sys.stdout.write("\x1b]2;~ChatUs~\x07")
	try:
		thread.start_new_thread(s.run,())
	except KeyboardInterrupt:
		pass



	def print_user():
		users = []
		for c in s.threads:
			if c.isguest == 0:
				users.append(c.username)
		users = sorted(users)
		return users

	def signal_handler(signal,frame):
		s.close()
		sys.exit(0)

	xmlserver = SimpleXMLRPCServer(("localhost",5001),logRequests=False)
	xmlserver.register_function(print_user,"list_user")
	try:
		thread.start_new_thread(xmlserver.serve_forever,())
		signal.signal(signal.SIGHUP , signal_handler)
		signal.pause()
	except KeyboardInterrupt:
		print "\nServer ChatUs stopped..."
		time.sleep(2)
		s.close()

