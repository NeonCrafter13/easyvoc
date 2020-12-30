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
    db="task",
    port=int(os.getenv("MYSQL_PORT")),
    autocommit=True
)
cursor = conn.cursor()


def search(name):
    query = """SELECT * FROM tasks WHERE name LIKE %s"""
    cursor.execute(query, [name])
    information = cursor.fetchmany(100)
    return information


def GetVoc(name):
    query = """SELECT * FROM vocs WHERE Deutsch = %s"""
    cursor.execute(query, [name])
    information = cursor.fetchone()
    if information == None:
        return None
    Deutsch = information[1]
    Englisch = information[2]
    Spanisch = information[3]

    Englisch = json.loads(Englisch)
    Spanisch = json.loads(Spanisch)

    return [Deutsch, Englisch, Spanisch]


def GetallTasks():
    query = """SELECT * FROM tasks"""
    cursor.execute(query)
    information = cursor.fetchmany(100)
    if information == None:
        return None
    return information


def GetTask(name):
    query = """SELECT * From tasks WHERE name = %s"""
    cursor.execute(query, [name])
    information = cursor.fetchone()
    if information == None:
        return None
    name = information[1]
    vocs = information[3]

    vocs = json.loads(vocs)

    vocs = set(random.choices(population = vocs, k = 25))

    return [name, vocs]


def GetTaskAuthor(name):
    query = """SELECT author From tasks WHERE name = %s"""
    cursor.execute(query, [name])
    information = cursor.fetchone()
    return information


def CreateTask(name: str, description: str, author: str, vocs: list, image: str):
    if GetTask(name) == None:
        query = """INSERT INTO tasks
        (name, description, vocs, author, image)
        VALUES (%s, %s, %s, %s, %s)"""
        values = (name, description, json.dumps(vocs), author, image)
        cursor.execute(query, values)
        conn.commit()
        return True
    return False


def AddVoc(name, Eng, Spa):
    a = GetVoc(name)
    if a == None:
        query = """INSERT INTO vocs
        (Deutsch, Englisch, Spanisch)
        VALUES (%s,%s,%s)"""
        values = (name, json.dumps([Eng]), json.dumps([Spa]))
        cursor.execute(query, values)
        conn.commit()
    else:
        if Eng != "":
            PreEnglisch = a[1]

            PreEnglisch.append(Eng)

            Eng = json.dumps(PreEnglisch)

            query1 = "UPDATE vocs SET Englisch = %s WHERE (Deutsch = %s)"
            values1 = (Eng,name)

            cursor.execute(query1, values1)
        if Spa != "":
            PreSpanisch = a[2]
            PreSpanisch.append(Spa)
            Spa = json.dumps(PreSpanisch)
            query2 = "UPDATE vocs SET Spanisch = %s WHERE (Deutsch = %s)"
            values2 = (Spa,name)
            cursor.execute(query2, values2)
        conn.commit()


def DeleteTask(username):
    query = "DELETE FROM `task`.`tasks` WHERE (`author` = %s);"
    cursor.execute(query, [username])
    conn.commit()
    return True


def DeleteTaskName(name):
    query = "DELETE FROM `task`.`tasks` WHERE (`name` = %s);"
    cursor.execute(query, [name])
    conn.commit()
    return True


def DeleteVoc(name):
    query = "DELETE FROM `task`.`vocs` WHERE (`Deutsch` = %s);"
    cursor.execute(query, [name])
    conn.commit()
    return True


def AnonymTask(username):
    query = "UPDATE tasks SET author = %s WHERE (author = %s)"
    values = ("Anonym", username)
    cursor.execute(query, values)
    conn.commit()
    return True


def GetCorrectVoc_Eng(name):
    query = "SELECT Englisch FROM vocs where (Deutsch = %s)"
    cursor.execute(query, [name])
    Eng = cursor.fetchone()
    if Eng == None:
        return None
    return json.loads(Eng[0])


def GetCorrectVoc_Spa(name):
    query = "SELECT Spanisch FROM vocs where (Deutsch = %s)"
    cursor.execute(query, [name])
    Spa = cursor.fetchone()
    if Spa == None:
        return None
    return json.loads(Spa[0])
