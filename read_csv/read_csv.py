import sqlite3
from pandas import DataFrame, read_csv
#import matplotlib.pyplot as plt
import pandas as pd 

def createTableFromCsv():
    file = "calc_test_export.csv"
    df:DataFrame = pd.read_csv(file, sep='\t')
    print(df)

    conn = sqlite3.connect( "testdb1.db" )
    # c = conn.cursor()
    #
    # sql = """DROP TABLE IF EXISTS test;"""
    # c.execute( sql )
    #
    # # sql = """ CREATE TABLE IF NOT EXISTS projects (
    # #                         id integer PRIMARY KEY,
    # #                         name text NOT NULL,
    # #                         begin_date text,
    # #                         end_date text
    # #                     ); """
    # sql = """ CREATE TABLE IF NOT EXISTS test (
    #                         Name text NOT NULL,
    #                         Vorname text,
    #                         'Alter' integer
    #                     ); """
    #
    # c.execute( sql )
    #c.execute("create table test (Name text, Vorname text, Alter integer);" )
    conn.commit()

    df.to_sql( "test", conn, if_exists='replace', index=False )
    conn.close()

def readTable():
    conn = sqlite3.connect("testdb1.db")
    c = conn.cursor()
    c.execute( """select * from test""")

def doTests():
    createTableFromCsv()



if __name__ == '__main__':
    doTests()




