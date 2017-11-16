import MySQLdb
db = MySQLdb.connect(host="localhost",user="root",passwd="123",db="chatroom")
cursor=db.cursor()
cursor.execute('select * from account where (ID like "test00");')
result = cursor.fetchall()
print result

db.close()
