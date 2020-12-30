import pymysql
import json
import random
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".envvar")

conn = pymysql.connect(
    host=os.getenv("MYSQL_HOST"),
    passwd=os.getenv("MYSQL_PASSWORD"),
    user=os.getenv("MYSQL_USER"),
    db="request",
    port=int(os.getenv("MYSQL_PORT")),
    autocommit=True
)
cursor = conn.cursor()

def CreatePermCreateRequest(user, why):
    query = """INSERT INTO permcreate_requests
    (user, why)
    VALUES (%s, %s)"""
    values = (user, why)
    cursor.execute(query, values)
    conn.commit()
    return True

def GetAllPermcreate():
    query = """SELECT * FROM permcreate_requests"""
    cursor.execute(query)
    return cursor.fetchmany(100)

def CreateReport(user, type, name, reason):
    query = """INSERT INTO reports
    (user, type, name, reason)
    VALUES (%s, %s, %s, %s)"""
    values = (user, type, name, reason)
    cursor.execute(query, values)
    conn.commit()
    return True

def GetAllReports():
    query = """SELECT * FROM reports"""
    cursor.execute(query)
    return cursor.fetchmany(100)

def DeleteReport(id: int):
    query = "DELETE FROM reports WHERE (`id` = %s);"
    cursor.execute(query, [id])
    conn.commit()
    return True

def GetReport(id):
    query = """SELECT * FROM reports WHERE (`id` = %s)"""
    cursor.execute(query, [id])
    information = cursor.fetchone()
    return information

def GetRequestsPermCreate(id):
    query = """SELECT * FROM permcreate_requests WHERE (`id` = %s)"""
    cursor.execute(query, [id])
    information = cursor.fetchone()
    return information

def DeleteRequestPermCreate(id: int):
    query = "DELETE FROM permcreate_requests WHERE (`id` = %s);"
    cursor.execute(query, [id])
    conn.commit()
    return True
