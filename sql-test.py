import sqlite3

conn = sqlite3.connect(r'c:\temp\example')

c = conn.cursor()

def createBase():
# Create table
    c.execute('''create table stocks
(date text, trans text, symbol text,
qty real, price real)''')

# Insert a row of data
#c.execute("""insert into stocks
#          values ('2006-01-05','BUY','RHAT',100,35.14)""")
c.execute('select * from stocks')

for row in c:
    print (row[1])

# Save (commit) the changes
conn.commit()

# We can also close the cursor if we are done with it
c.close()
