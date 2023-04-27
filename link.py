import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir="C:\oracle_client_19") # init Oracle instant client 位置
connection = cx_Oracle.connect('GROUP6', 'HWoXLK9f2n', cx_Oracle.makedsn('140.117.69.60', 1521, service_name='ORCLPDB1'))
cursor = connection.cursor()

