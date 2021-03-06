import pymysql

def connect(user,password):
    connection = pymysql.connect(   host='localhost',
                                    user=user,
                                    #user='farmrisk',
                                    database='farmrisk',
                                    password=password,
                                    #password='zRC56%jT#**X',
                                    charset='utf8mb4',
                                    port=5136
                                )
    return connection

def disconnect(connection):
    connection.close()

def generate(connection, table):
    filename = 'data/farmrisk_db_' + table + '.txt'
    # generate database from existing files
    with open(filename) as f:
        lines = f.readlines()
        with connection.cursor() as cursor:
            for sql in lines:
                print(sql) # debug line
            #with connection.cursor() as cursor:
                cursor.execute(sql)
        #with connection.cursor() as cursor:
            if table != "drop_create":
                sql = "select * from " + table
                cursor.execute(sql)
                print(cursor.fetchall())
            connection.commit()

# program body
connection = connect('root','3z2XVra2HJHx') # later, prompt for these values
print("Executing SQL queries to build database.\n")
generate(connection, 'drop_create')
generate(connection, 'chemicals')
disconnect(connection)

