import os
import  sys
import sqlite3
from sqlite3 import  Error


class Interface():
    datapath = "./data"
    database = ""
    def __init__(self):
        self.cursor =  None
        self.__conn = None

    def __skeleton(conn, priority):
        """
        Query tasks by priority
        :param conn: the Connection object
        :param priority:
        :return:
        """
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE priority=?", (priority,))

        rows = cur.fetchall()

        for row in rows:
            print(row)






class dbconfig(Interface):
    def __init__(self):
        Interface.__init__(self)
        self.database = "appconfig/config.db"
        self.conn = sqlite3.connect(os.path.join(self.datapath, self.database))


class dbapp(Interface):
    def __init__(self, jobnumber =10000 ):
        Interface.__init__(self)
        self.__jobnumber = jobnumber
        self.database  = "seasnake/{}.db".format(self.__jobnumber)
        self.conn = sqlite3.connect(os.path.join(self.datapath, self.database))





