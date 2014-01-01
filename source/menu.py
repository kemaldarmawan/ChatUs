import sys
import getpass
import os

def MenuForm():
	os.system("clear")
	print "Enter Command:"
	print "(1). Login"
	print "(2). Register"
	print "(3). Enter as guest"
	print(">>>"),
	cmd = raw_input()
	return cmd

def LoginForm():
	os.system("clear")
	print "---LOGIN---"
	print("Username:"),
	username = raw_input()
	password = getpass.getpass()
	return username,password

def RegisterForm():
	os.system("clear")
	print "---REGISTER---"
	print("Username:"),
	username = raw_input()
	password = getpass.getpass()
	return username,password