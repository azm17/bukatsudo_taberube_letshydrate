import configparser
import mysql.connector

config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

SQLserver_host = config_ini['DEFAULT']['SQLserver_host']
SQLserver_port = config_ini['DEFAULT']['SQLserver_port']
database_name  = config_ini['DEFAULT']['database_name']
sql_userid     = config_ini['DEFAULT']['sql_userid']
sql_userpass   = config_ini['DEFAULT']['sql_userpass']

def sql_run_query(sql_query):
    conn = mysql.connector.connect(
        host = SQLserver_host,
        port = SQLserver_port,
        user = sql_userid,
        password = sql_userpass,
        database = database_name,
    )
    cur = conn.cursor()
    connected = conn.is_connected()
    if (not connected):
        conn.ping(True)
    cur.execute(sql_query)

    return cur.fetchall()

def sql_update_query(sql_query):
    conn = mysql.connector.connect(
        host = SQLserver_host,
        port = SQLserver_port,
        user = sql_userid,
        password = sql_userpass,
        database = database_name,
    )
    cur = conn.cursor()
    connected = conn.is_connected()
    if (not connected):
        conn.ping(True)
    
    cur.execute(sql_query)
    conn.commit()

    return cur.fetchall()