from socket import *
import thread
import sys
import xmlrpclib

class ChatClient:
    def __init__(self, host='localhost',port=5000, mxbf=4096):
        self.addr = (host,port)
        self.mxbf = mxbf
        self.sock = None
		
    def connect(self,username):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.addr))
        self.sock.send(username)
        self.listener = thread.start_new_thread(self.__listen__,())
		
    def disconnect(self):
        #self.say('@disconnect')
        self.sock.close()
	
    def say(self, msg):		
        self.sock.send(msg)
	
    def __listen__(self):
        while self.sock:
            try:
                print self.sock.recv(self.mxbf)
            except:
                print "Disconnected from server!"
                self.sock = None

if __name__ == "__main__":
    c = ChatClient()
    c.connect(sys.argv[1])
    proxy = xmlrpclib.ServerProxy("http://localhost:5001/")
    print proxy.list_user()
    while True:
        msg = raw_input()
        try:
            c.say(msg)
        except:
            print "Disconnected from server!"
            sys.exit(1)
