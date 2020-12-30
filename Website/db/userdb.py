import pymysql
import hashlib
import string
import json
import random
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".envvar")

conn = pymysql.connect(
    host=os.getenv("MYSQL_HOST"),
    passwd=os.getenv("MYSQL_PASSWORD"),
    user=os.getenv("MYSQL_USER"),
    db="user",
    port=int(os.getenv("MYSQL_PORT")),
    autocommit=True
)
cursor = conn.cursor()

def Get_User(name):
    query = """SELECT * FROM users WHERE username = %s"""
    cursor.execute(query, [name])
    information = cursor.fetchone()
    return information

def SetPermCreate(name):
    query = "UPDATE users SET permcreate = 1 WHERE (`username` = %s);"
    cursor.execute(query, [name])
    conn.commit()
    return True

def SetAuthentication(name):
    query = "UPDATE users SET `email authorizated` = 1 WHERE (`username` = %s);"
    cursor.execute(query, [name])
    conn.commit()
    return True

def Get_User_Email(email):
    query = """SELECT * FROM users WHERE email = %s"""
    cursor.execute(query, [email])
    information = cursor.fetchone()
    return information

def Get_User_id(id):
    query = """SELECT * FROM users WHERE id = %s"""
    cursor.execute(query, [id])
    information = cursor.fetchone()
    return information

def Create_User(name, password, email):
    createperm = False
    reportperm = True
    if not Get_User(name) == None:
        a = True
        return "Benutzername bereits vergeben!"
    if not Get_User_Email(email) == None:
        a = True
        return "Email bereits vergeben!"
    else:
        a = False
    if a == False:
        h = hashlib.new("whirlpool")
        stringLength = 16
        characters = string.ascii_letters + string.digits + string.punctuation
        salt = ''.join(random.choice(characters) for i in range(stringLength))
        password = password + salt
        h.update(password.encode())
        password = h.hexdigest()
        query = """INSERT INTO users
        (username, pwd, email, permcreate, permreport, salt)
        VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (name, password, email, createperm, reportperm, salt)
        cursor.execute(query, values)
        conn.commit()
        succesfull = True
    else:
        succesfull = False
    return succesfull

def Change_Pwd(name, old_pwd, new_pwd):
    information = Get_User(name)
    h = hashlib.new("whirlpool")
    old_pwd = old_pwd + information[8]
    h.update(old_pwd.encode())
    old_pwd = h.hexdigest()
    if information[2] == old_pwd:
        query = """UPDATE users SET pwd = %s, salt=%s WHERE username = %s;"""
        h = hashlib.new("whirlpool")
        stringLength = 16
        characters = string.ascii_letters + string.digits + string.punctuation
        salt = ''.join(random.choice(characters) for i in range(stringLength))
        new_pwd = new_pwd + salt
        h.update(new_pwd.encode())
        new_pwd = h.hexdigest()
        cursor.execute(query, [new_pwd, salt, name])
        succesfull = True
    else:
        succesfull = False
    conn.commit()
    return succesfull

def Change_Pwd_without_oldpwd(name, new_pwd):
    h = hashlib.new("whirlpool")
    stringLength = 16
    characters = string.ascii_letters + string.digits + string.punctuation
    salt = ''.join(random.choice(characters) for i in range(stringLength))
    new_pwd = new_pwd + salt
    h.update(new_pwd.encode())
    new_pwd = h.hexdigest()
    query = "UPDATE users SET pwd = %s, salt = %s WHERE username = %s"
    cursor.execute(query, [new_pwd, salt, name])
    conn.commit()
    return True

def Change_Email(name, email, pwd):
    information = Get_User(name)
    h = hashlib.new("whirlpool")
    pwd = pwd + information[8]
    h.update(pwd.encode())
    pwd = h.hexdigest()
    if information[2] == pwd:
        if Get_User_Email(email) == None:
            query = """UPDATE users SET email = %s WHERE username = %s;"""
            cursor.execute(query, [email, name])
            query = """UPDATE users SET `email authorizated` = 0 WHERE username = %s;"""
            cursor.execute(query, [name])
            conn.commit()
            return True
        else:
            return "Email bereits vergeben"
    else:
        return "Falsches Passwort"

def Login(name, pwd):
    information = Get_User(name)
    h = hashlib.new("whirlpool")
    pwd = pwd + information[8]
    h.update(pwd.encode())
    pwd = h.hexdigest()
    if not information == None:
        if information[2] == pwd:
            succesfull = True
        else:
            succesfull = False
    else:
        succesfull = False

    return succesfull

def Delete_Account(name):
    query = "DELETE FROM `user`.`users` WHERE (`username` = %s);"
    cursor.execute(query, [name])
    conn.commit()
    return True

# conn.commit()
# conn.close()
