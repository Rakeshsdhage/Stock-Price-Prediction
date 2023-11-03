import sqlite3
conn = sqlite3.connect("stock.db")
print("opened database successfully")

conn.execute("CREATE TABLE adminlogin (ausername varchar,apassword varchar)")
conn.execute("CREATE TABLE faq (question varchar, answer varchar)")
conn.execute("CREATE TABLE signup (uname varchar,uphone varchar,username varchar,upassword varchar)")


print("table created successfully")
conn.close()
