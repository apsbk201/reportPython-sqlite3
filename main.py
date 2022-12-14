#!/usr/bin/python3
import sqlite3
import logging
import getpass
import hashlib
import pandas as pd
import openpyxl
from datetime import datetime

logsFile = 'logs.log'
db = 'report.db'

con = sqlite3.connect(db)
cur = con.cursor()

logging.basicConfig(filename=logsFile, encoding='utf-8', level=logging.logProcesses,
                        format=(f'%(asctime)s {getpass.getuser()} : %(levelname)s : %(message)s'))

global userlogin
userlogin = False
global user
user = ' '
#---------------------- Create Table ------------------------------
def creatTable_user():
    try :
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            fname VARCHAR(255) NOT NULL,
            lname VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            position VARCHAR(255) NOT NULL,
            uname VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
            )
        """)
        logging.debug('Create User Table')
        print('Create Table User ')
    except Exception as e:
        logging.error(e)
        print(e)

def creatTable_report():
    try :
        cur.execute("""
        CREATE TABLE IF NOT EXISTS report (
            id INTEGER PRIMARY KEY,
            date VARCHAR(255) NOT NULL,
            time VARCHAR(255) NOT NULL,
            topic TEXT NOT NULL,
            detail TEXT NOT NULL,
            result TEXT NOT NULL,
            commander TEXT NOT NULL,
            assistant TEXT NOT NULL,
            uname VARCHAR(255) NOT NULL
            )
        """)
        logging.debug('Create New report Table')
    except Exception as e:
        logging.error(e)
        print(e)

#---------------------- Insert User ------------------------------
def insertUserDB(fname, lname, email, position, uname, password):
    try :
        cur.execute("INSERT INTO user (fname, lname, email, position, uname, password)VALUES (?,?,?,?,?,?)", \
                    (fname, lname, email, position, uname, password))

        con.commit()
        print("Insert user Success")
        logging.debug(f'Insert user name {uname}')
    except Exception as e:
        logging.error(e)
        print(e)

def insertUser():
    print('Add New User.')
    fname = input('First name: ')
    lname = input('Last name: ')
    email = input('Email : ')
    position = input('Position: ')
    uname = input('Login name: ')
    #password = input('Password: ')
    password = getpass.getpass('Password: ')    # pycharm can't run getpass
    password = hashlib.sha256(password.encode()).hexdigest()
    insertUserDB(fname, lname, email, position, uname, password)

#---------------------- Insert data ------------------------------
def insertReport(ddate, ttime, topic, detail, result, commander, assistant, uname):
    try :
        cur.execute("INSERT INTO report (date, time, topic, detail, result, commander, "
                    "assistant, uname)VALUES (?,?,?,?,?,?,?,?)", \
                    (ddate, ttime, topic, detail, result, commander, assistant, uname))

        con.commit()
        print(ddate, ttime, topic, detail, result, commander, assistant)
        print("Success")
        logging.debug(f'Insert data from {user}')
    except Exception as e:
        logging.error(e)
        print(e)

def insert():
    try:
        dt = datetime.now()
        ddate1 = dt.strftime("%Y-%m-%d")
        ttime1 = dt.strftime("%H:%M:%S")
        #------------------- Input -------------------
        ddate = input('Date yyyy-mm-dd: ')
        if ddate == '':
            ddate = ddate1
        ttime = input('Time HH:MM:SS: ')
        if ttime == '':
            ttime = ttime1
        topic = input('Topic : ')
        detail = input('Detail :')
        result = input('Result: ')
        commander = input('Commander:')
        assistant = input('Assistant: ')
        uname = user
        insertReport(ddate,ttime,topic,detail,result,commander,assistant,uname)
    except Exception as e:
        print(e)
        logging.error(e)

global num_login
num_login = 0

def login():
    global user
    global num_login
    print('Wellcome to your report Please Login')
    user = input('Username: ')
    password = getpass.getpass('Password: ')    # pycharm can't run getpass
    # password = input('Password: ')
    password = hashlib.sha256(password.encode()).hexdigest()
    cur.execute("SELECT * FROM user WHERE uname=? AND password=?",(user,password))
    if cur.fetchall():
        print('Your in')
        return True
    else:
        print("It's Wrong!! Try Again")
        num_login += 1
        if num_login >= 3 :
            exit()
        login()

def readAllDb():
    try:
        sql = """SELECT * FROM report WHERE uname=?"""
        res = cur.execute(sql, (user,))
        # for row in res:
        #     print(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],'\n')
        df = pd.DataFrame(res, columns=['id','date','time','topic','detail','result','commander','assistant','User'])
        print(df)
        ct = input('Save to Excel (y/n) ? ').lower()
        if ct == 'y':
            exportToExcel(df)
        else:
            pass
    except Exception as e:
        print(e)

def readFromDate():
    dt = datetime.now()
    ddate1 = dt.strftime("%Y-%m-%d")
    ddate = input('Date yyyy-mm-dd: ')
    if ddate == '':
        ddate = ddate1
    sql = "SELECT * FROM report WHERE date=? AND uname=?"
    res = cur.execute(sql,(ddate,user,))
    df = pd.DataFrame(res, columns=['id','date','time','topic','detail','result','commander','assistant','User'])
    print(df)
    ct = input('Save to Excel (y/n) ? ').lower()
    if ct == 'y':
        exportToExcel(df)
    else:
        pass

def readFromLast():
    sql = "SELECT * FROM report WHERE uname=? ORDER BY ROWID DESC"
    res = cur.execute(sql,(user,))
    num_row = input('How many row ? :')
    if num_row == '':
        num_row = 5
    print(f'Show {num_row} by last time')
    df = pd.DataFrame(res, columns=['id','date','time','topic','detail','result','commander','assistant','User'])
    print(df)
    ct = input('Save to Excel (y/n) ? ').lower()
    if ct == 'y':
        exportToExcel(df)
    else:
        pass
#def readFromDayToexcel():
#    try:
#        dt = datetime.now()
#        ddate1 = dt.strftime("%Y-%m-%d")
#        ddate = input('Date yyyy-mm-dd: ')
#        if ddate == '':
#            ddate = ddate1
#        sql = "SELECT date,time,topic,detail,result,commander,assistant FROM report WHERE date=?"
#        res = cur.execute(sql,(ddate,))
#        df = pd.DataFrame(res, columns=['date','time','topic','detail','result','commander','assistant'])
#        print(df)
#        ct = input('Save to Excel (y/n) ? ')
#        if ct == 'y':
#            filename = f"{ddate}_{username}.xlsx"
#            df.to_excel(filename, index=False)
#            print(df)
#            print(f"Successfull {filename}")
#            logging.debug(f'Create {filename}')
#
#    except Exception as e:
#        logging.error(e)
#        print(e)

def exportToExcel(df):
    try:
        dt = datetime.now()
        ddate = dt.strftime("%Y-%m-%d")
        ttime1 = dt.strftime("%H:%M:%S")
        fileInputName= input('File name : ')
        if fileInputName == '':
            fileInputName = ttime1

        filename = f"{ddate}_{fileInputName}.xlsx"
        df.to_excel(filename, index=False)
        print(f"Successfull {filename} By {user}")
        logging.debug(f'Create {filename} By {user}')

    except Exception as e:
        logging.error(e)
        print(e)
def deleteById():
    try :
        id = input('Input id row for delete : ')
        read = "SELECT * FROM report WHERE id=?"
        # cur.execute(read,(id,))# for row in res:
        res = cur.execute(read,(id))
        df = pd.DataFrame(res, columns=['id','date','time','topic','detail','result','commander','assistant','User'])
        print(df)
        ct = input('Delete this report ? (y/n):')
        if ct == 'y':
            sql = 'DELETE FROM report WHERE id=?'
            cur.execute(sql,(id,))
            con.commit()
            logging.debug(f'Delete report id:{id} By {user}')
            print(f'id:{id} Deleted')
        else:
            print(f'Not Delete this report ')

    except Exception as e:
        print(e)
        logging.error('Delete report by id ',e)

def deleteAll():
    try :
        ans = input('Delete All Data ? (y/n)')
        if ans == 'y':
            sql = 'DELETE FROM report'
            cur.execute(sql)
            con.commit()
            logging.debug(f'Delete All By {user}')
            print('Deleted')

    except Exception as e:
        print(e)
        logging.error('delete all ',e)

#-------------- Check first time and Create table ------------------
try:
    res = cur.execute("SELECT id FROM user")
    # print(res)
except:
    # print("None")
    creatTable_user()
    insertUser()
    creatTable_report()

userlogin = login()

while userlogin:
    menu1 = input('(1)Write report (2)Read Report (3)Other (x)Exit :').lower()
    if menu1 == '1':
        insert()
    elif menu1 == '2':
        menuRead = input('(1)Read ALL (2)Read From Date (3)Read From Last :')
        if menuRead == '1':
            readAllDb()
        elif menuRead == '2':
            readFromDate()
        elif menuRead == '3':
           readFromLast()
    elif menu1 == '3':
        menu2 = input('(1)Delete Report (2)Add User (x)Exit :').lower()
        if menu2 == '1':
            deleteById()
        elif menu2 == '2':
            insertUser()
        elif menu2 == 'x':
            exit()
        else:
            print('Missing!!!')
    elif menu1 == 'x':
        exit()
    else:
        print('Missing!!!')