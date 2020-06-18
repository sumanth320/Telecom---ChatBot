# Import the required packages.
import sqlite3
import pandas as pd

# create a connection to the DB and a cursor:
# If the Db is already existing it will connect, if not it will create one
db_connect = sqlite3.connect("Telebot.db")
db_cur = db_connect.cursor()
print("connection and cursor created successfully")

# Create Budget: 3 columns -->ID(Auto Incremented),budget (customer budget),load_date (current date)
db_cur.execute("drop table IF EXISTS budget")
db_connect.commit()
db_cur.execute("""create table budget
                (
                id integer Primary key Autoincrement NOT NULL,
                budget varchar2(4000) NOT NULL,
                load_date date
                );""")

# Create Table "datalimit":id(Auto Incremented),data (customer data requirement),load_date (current date)
db_cur.execute("drop table IF EXISTS data")
db_connect.commit()
db_cur.execute("""create table data
                (
                id integer Primary key Autoincrement NOT NULL,
                data varchar(255) NOT NULL,
                load_date date
                );""")

# Create Table "plan_type": 3 columns--> id(Auto Incremented),plan_type (prepaid,postpaid),load_date (current_date)
db_cur.execute("drop table IF EXISTS plan_type")
db_connect.commit()
db_cur.execute("""Create table plan_type
                (
                id integer Primary key Autoincrement NOT NULL,
                plan_type varchar(255) NOT NULL,
                load_date date
                );""")

# Create table Rate_Plans : 14 columns
db_cur.execute("drop table IF EXISTS rate_plans")
db_connect.commit()
df = pd.read_csv('Telecom_Tariff.csv',
                 names=['RATEPLAN_TYPE', 'VENDOR', 'RATEPLAN_NAME', 'RECURRING_FEE', 'ONEOFF_FEE', 'DATA_LIMIT',
                        'RECOMMENDATION',
                        'INTERNET_INFO', 'EU_ROAMING_INFO', 'TELEPHONY_SMS_MMS_INFO', 'RUNNING_TIME_INFO',
                        'NOTICE_PERIOD_INFO', 'AUTO_RENEWAL_INFO', 'URL_LINK'], header=0,index_col=False)

df.to_sql("rate_plans", db_connect)

# Close connection and cursor.
db_cur.close()
db_connect.close()
print("Db and tables created successfully")
print("connection and cursor closed successfully")
