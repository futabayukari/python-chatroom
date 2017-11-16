import socket
import threading
import time
import MySQLdb
bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip,bind_port))
server.listen(5)

global chat_users
global online_user
global messageboard
global chat_user_connects
chat_users = []
online_user = []
messageboard = []
chat_user_connects = []

print "[*] Listening on %s:%d" % (bind_ip,bind_port)

def Register(client, command):
	
	a = command.split(":")
	b = a[1].split(",")
	userID = b[0]

	db = MySQLdb.connect(host="localhost",user="root",passwd="123",db="chatroom")
	cursor=db.cursor()
	db_command = 'select * from account where (ID = "'+userID+'");'
	cursor.execute(db_command)
	result = cursor.fetchall()
	


	if(len(result) > 0):
		client.send("the same id")
	else:
		db_command = 'INSERT INTO account(ID,PW) VALUES ("' + userID+'","'+b[1]+'");'
		cursor.execute(db_command)
		db.commit()
		client.send("Register Succeed")

	db.close()
	return command

def login(client, command):

	print "start login"
	a = command.split(":")
	b = a[1].split(",")
	userID = b[0]
	userpw = b[1]

	db = MySQLdb.connect(host="localhost",user="root",passwd="123",db="chatroom")
	cursor=db.cursor()
	db_command = 'select * from account where (ID = "'+userID+'" && PW = "'+userpw+'");'
	cursor.execute(db_command)
	result = cursor.fetchall()

	if len(result) > 0:
		client.send("login Succeed")
		online_user.append(userID)
	else:
		client.send("login Failed")
	print "end Login"
	return command

def chat(client, command):
	global messageboard
	print "start chat"
	a = command.split(":")
	b = a[1].split(",")
	ip0 = b[0]
	port0 = int(b[1])
	client0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client0.connect((ip0,port0))
	global chat_user_connects
	chat_user_connects.append(client0)	
	while True:
		request = client.recv(4098)
		if(len(request) > 0 and request != "end"):
			messageboard.append(request)
		elif(request == "end"):
			chat_user_connects.remove(client0)
			client0.send("Disconnect!!")
			client0.close()
			break
			
	return command


def chat_room():
	global messageboard
	global chat_user_connects
	while True:
		if(len(messageboard) > 0):
			print "send start"
			print messageboard
			for client in chat_user_connects:
				client.send(messageboard[0])
			print messageboard
			messageboard.pop(0)
			print "send end"
		
def show_online_users(client_socket):
	global online_user
	message = ";".join(online_user)
	client_socket.send(message)


def handle_client(client_socket):
	global online_user
	while	True:
		request = client_socket.recv(1024)
		if "Disconnect!!" in request:
			user = request.split(";")[1]
			client_socket.close()
			if user in online_user:
				online_user.remove(user)
			print "Disconnect!!"
			break
		else:
			Command_type = request.split(":")
			if(Command_type[0] == "Register"):
				Register(client_socket, request)
			elif(Command_type[0] == "login"):
				login(client_socket, request)
			elif(Command_type[0] == "chat"):
				print "chat at"+request
				chat(client_socket, request)
			elif "online" in request:
				show_online_users(client_socket)
			print "[*] Received: %s" % request



client_handler2 = threading.Thread(target=chat_room,args=())
client_handler2.start()

try:
	while	True:
		client,addr = server.accept()
		print "[*] Accept connection from: %s:%d" % (addr[0],addr[1])
		client_handler = threading.Thread(target=handle_client,args=(client,))
		client_handler.start()
		
except KeyboardInterrupt:
	server.close()
	print "end"
