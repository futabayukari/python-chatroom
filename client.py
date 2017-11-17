import socket
import threading
bind_ip = "127.0.0.1"
bind_port = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((bind_ip,bind_port))
global chat_port
global chat_status
global chat_server_status
global chat_server
global userID
userID="test00"
status = False
chat_status = False
chat_server_status = True
def Register(client):
	print "[*]new ID:"
	ids = raw_input()
	print "[*]new password:"
	pw = raw_input()
	message = "Register:"+ids+","+pw
	client.send(message)
	response = client.recv(4096)
	print response
	return False

def login(client):
	global userID
	print "[*]ID:"
	ids = raw_input()
	print "password:"
	pw = raw_input()
	message = "login:"+ids+","+pw
	client.send(message)
	response = client.recv(4096)
	if(response == "login Succeed"):
		status = 1
		print "login succeed client"
		userID = ids
		return True
	else:
		print "login failed client"
		return False
def chat_Room(client):
	print "chat_Room  start"
	global chat_status
	global userID
	global chat_port
	global chat_server_status
	global chat_server
	chat_status = True
	if chat_server_status:
		bind_ip = "0.0.0.0"
		chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		chat_server.bind((bind_ip,int(chat_port)))
		chat_server.listen(5)
		chat_server_status = False

	client.send("chat:0.0.0.0,"+chat_port)
	client_chat,addr = chat_server.accept()
	
	print "[*] Accept connection from: %s:%d" % (addr[0],addr[1])
	client_handler = threading.Thread(target=handle_client,args=(client_chat,))
	client_handler.start()
	while True:
		try:
			print "user:"
			command = raw_input()
			if(command != "end"):
				client.send(userID+":"+command)
			elif(command == "end"):
				client.send(command)
				chat_status = False
				break
		except:
			client.send("Disconnect!!;"+userID)
			print "chat end"
			chat_status = False
			break
	chat_status = False
	print "chat_Room end"
def handle_client(client_socket):
	global chat_status
	try:
		while chat_status:
			try:
				request = client_socket.recv(1024)
				if request != "Disconnect!!" and len(request) > 0:
					print request
				elif request == "Disconnect!!":
					client_socket.close()
			except KeyboardInterrupt:
				client_socket.close()
				print "end"
		
		client_socket.close()
	except KeyboardInterrupt:
		client_socket.close()
		print "end"
def show_all_user(client):
	client.send("online")
	response = client.recv(4096)
	userList = response.split(";")
	for user in userList:
		print user
	
def status_true(client, command):
	if "chat" in command:
		chat_Room(client)
	elif "online" in command:
		show_all_user(client)

	return True

def login_or_register(client, command):
	print "22222222"
	rv = False
	request = command.split(":")[0]
	if(request == "Login"):
		rv = login(client)
	elif (request == "Register"):
		rv = Register(client)
	return rv


print "chat port:"
chat_port = raw_input()
try:
	while	True:
		if(status == False):
			print "[*]Login/Register:"
		else:
			print "[*]Chat Room/online users:"
		try:
			command = raw_input()
			if(status == False):
				status = login_or_register(client, command)
			else:
				status = status_true(client, command)
			
		except:
			client.send("Disconnect!!;"+userID)
			print "end00"
			break;
except KeyboardInterrupt:
	client.send("Disconnect!!;"+userID)
	print "end"

