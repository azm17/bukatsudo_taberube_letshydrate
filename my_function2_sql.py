# -*- coding: utf-8 -*-
"""
Created on Fri May 17 12:52:30 2019

@author: Azumi Mamiya
         Daiki Miyagawa

version: v1.1
"""
import configparser
# サーバ環境ファイル読込み
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')
# サーバ情報設定
server_address = config_ini['APP']['SERVER_ADDRESS']

import my_function_mysql as my_func_sql
import datetime
import csv
import random, string

def init_tenki_dic():
    tmp_dic = {}
    sql_query  = " SELECT CODE, VAL1"
    sql_query += " FROM   MST_KBN_CODE"
    sql_query += " WHERE   CLASS_CODE = 'WEATHER'"
    rtn_query = my_func_sql.sql_run_query(sql_query)

    for row in rtn_query:
        tmp_dic[row[0]] = row[1]
    return tmp_dic

# すべてのユーザーのIDとパスを表示，my_function内のみ使用
def get_user_dic():
    user_dic = {}

    sql_query  = " SELECT ID, PASSWORD"
    sql_query += " FROM   MST_USER_ID"
    rtn_query = my_func_sql.sql_run_query(sql_query)

    for row in rtn_query:
        user_dic[row[0]] = row[1]
    return user_dic

# 全てのユーザーの全ての情報を取得，my_function内のみ使用
def get_user_info():
    user_info = []
    
    sql_query  = " SELECT ID, PASSWORD, USER_CLASS, NAME, ORG_CODE, ENTRY_YEAR"
    sql_query += " FROM   MST_USER_ID"
    rtn_query = my_func_sql.sql_run_query(sql_query)

    for row in rtn_query:
        user_info.append({'id'       : row[0],
                          'password' : row[1],
                          'type'     : row[2],
                          'rname'    : row[3],
                          'org'      : row[4],
                          'year'     : row[5]})
    return user_info

def sql_ALLuser_profile(userid,userpass):
    user_prof = {}

    sql_query  = " SELECT A.ID, A.NAME, A.USER_CLASS, A.ACTIVE_VALUE, A.ORG_CODE, A.ENTRY_YEAR ,B.ORG_NAME"
    sql_query += " FROM   MST_USER_ID A"
    sql_query += "       ,MST_ORG B"
    sql_query += " WHERE (A.ORG_CODE = (SELECT X.ORG_CODE "
    sql_query += "                      FROM MST_USER_ID X"
    sql_query += "                      WHERE X.ID = '{}'".format(userid)
    sql_query += "                      AND   X.PASSWORD = '{}'".format(userpass)
    sql_query += "                      AND   X.USER_CLASS = 2)"
    sql_query += "        OR 'ADM'   = (SELECT X.ORG_CODE "
    sql_query += "                      FROM MST_USER_ID X"
    sql_query += "                      WHERE X.ID = '{}'".format(userid)
    sql_query += "                      AND   X.PASSWORD = '{}'".format(userpass)
    sql_query += "                      AND   X.USER_CLASS = 0))"
    sql_query += " AND B.ORG_CODE = A.ORG_CODE"
    rtn_query = my_func_sql.sql_run_query(sql_query)

    for row in rtn_query:
        user_prof[row[0]] = {
                 'rname':row[1],
                 'type' :row[2],
                 'active_val'  :row[3],
                 'org'  :row[4],
                 'year'  :row[5],
                 'org_name'  :row[6]
                 }
    
    return user_prof

def sql_chk_userid(userid):
    sql_query  = " SELECT 'X'"
    sql_query += " FROM   MST_USER_ID "
    sql_query += " WHERE  ID       = '{}'".format(userid)
     
    rtn_query = my_func_sql.sql_run_query(sql_query)

    if len(rtn_query) == 0 :
        return False
    else:
        return True

def sql_get_user_profile(userid, userpass):
    user_prof = {}

    sql_query  = " SELECT ID, NAME, USER_CLASS, ACTIVE_VALUE, ORG_CODE "
    sql_query += " FROM   MST_USER_ID "
    sql_query += " WHERE  ID       = '{}'".format(userid)
    sql_query += " AND    PASSWORD = '{}'".format(userpass)
     
    rtn_query = my_func_sql.sql_run_query(sql_query)

    for row in rtn_query:
        user_prof[row[0]] = {
                 'rname':row[1],
                 'type' :row[2],
                 'active_val'  :row[3],
                 'org'  :row[4],
                 }
    
    return user_prof


# 組織リスト取得
def get_org():
    org_dic = {}
    sql_query  = " SELECT ORG_CODE,ORG_NAME"
    sql_query += " FROM   MST_ORG"
    rtn_query = my_func_sql.sql_run_query(sql_query)

    for row in rtn_query:
        org_dic[row[0]] = {'org_name':row[1]}
    
    return org_dic

# 組織リスト取得
def get_org2(userid,userpass):
    org_dic = []
    sql_query  = " SELECT ORG_CODE,ORG_NAME"
    sql_query += " FROM   MST_ORG A"
    sql_query += " WHERE  A.HIDDEN_FLG=0"

    sql_query += " AND   (A.ORG_CODE = (SELECT X.ORG_CODE "
    sql_query += "                      FROM MST_USER_ID X"
    sql_query += "                      WHERE X.ID = '{}'".format(userid)
    sql_query += "                      AND   X.PASSWORD = '{}')".format(userpass)
    sql_query += "        OR 'ADM'   = (SELECT X.ORG_CODE "
    sql_query += "                      FROM MST_USER_ID X"
    sql_query += "                      WHERE X.ID = '{}'".format(userid)
    sql_query += "                      AND   X.PASSWORD = '{}'))".format(userpass)

    rtn_query = my_func_sql.sql_run_query(sql_query)

    for row in rtn_query:
        org_dic.append({'org_code':row[0],'org_name':row[1]})
    
    return org_dic

def get_org_newaccount():
    org_dic = {}
    sql_query  = " SELECT ORG_CODE,ORG_NAME"
    sql_query += " FROM   MST_ORG"
    sql_query += " WHERE  HIDDEN_FLG=0"
    rtn_query = my_func_sql.sql_run_query(sql_query)

    for row in rtn_query:
        org_dic[row[0]] = {'org_name':row[1]}
    
    return org_dic



#ログイン処理
def kakunin(user_name, user_pass):
    connected = False
    user_dic = get_user_dic()
    if user_name in user_dic.keys():
        if user_pass == user_dic[user_name]:
            connected = True
    return connected

def admin_kakunin(user_name, user_pass):
    connected = False
    user_info = get_user_info()
    for i in range(len(user_info)):
        if user_name == user_info[i]['id'] \
            and user_pass == user_info[i]['password'] \
                and str(user_info[i]['type']) == '0':
            connected = True
            break
    return connected

def admin_coach_kakunin(user_name, user_pass):
    connected = False
    user_info = get_user_info()
    for i in range(len(user_info)):
        if user_name == user_info[i]['id'] \
            and user_pass == user_info[i]['password'] \
                and user_info[i]['type'] == 0 or 2:
            connected = True
            break
    return connected

# 管理者のリストを取得
def get_admin():
    user_info = get_user_info()
    admin = []
    for i in range(len(user_info)):
        if user_info[i]['type'] == '0':
            admin.append(user_info[i]['id'])
    return admin

def sql_data_send(user_name,
                  user_pass,
                  bweight,
                  aweight,
                  training,
                  time,
                  water,
                  weather,
                  humidity,
                  temp):
    
    user_dic = get_user_dic()
    if user_pass == user_dic[user_name]:
        user_dic = get_user_dic()
        
        sql_query  = " INSERT INTO TBL_DATA_TRAINING"
        sql_query += "  (USER_ID,TRAINING_YMD,TRAINING_TIME,WEATHER_CODE, HUMIDITY,"
        sql_query += "  TRAINING_CONTENT,TRAINING_HOUR, WEIGHT_BEFORE,WEIGHT_AFTER,INTAKE_WATER,TEMPERATURE) "
        sql_query += " VALUES ('{}', CURDATE(), CURRENT_TIME(), {}, {},'{}',{},{},{},{},{})".format( user_name, weather, humidity,training, time, bweight, aweight, water,temp)

        rtn_query = my_func_sql.sql_update_query(sql_query)
        
        return  'OK'
    return  'NG'

def sql_data_get(user_nm):
    #user_name ←のアカウントを使って
    #user_nm ←のデータを取得
    data_list = []
    sql_query = ''' SELECT USER_ID,TRAINING_YMD, WEATHER_CODE, HUMIDITY, TRAINING_CONTENT,TRAINING_HOUR,
                           WEIGHT_BEFORE,WEIGHT_AFTER,INTAKE_WATER,TEMPERATURE FROM TBL_DATA_TRAINING WHERE USER_ID = '{}' 
                '''.format(user_nm)
    rtn_query = my_func_sql.sql_run_query(sql_query)

    for row in rtn_query:
        data_list.append({'day'     :row[1],#日
                          'tenki'   :row[2],#天気
                          'shitsudo':row[3],
                          'contents':row[4],#トレーニング内容
                          'time'    :row[5],#時間
                          'wb'      :row[6],#運動前体重
                          'wa'      :row[7],#運動後体重
                          'moi'     :row[8],#飲水量
                          'temp'    :row[9]})#湿度
    
    data_list.sort(key = lambda x:x['day'])
    
    return data_list

def sql_data_get_latest_all(userid, userpass):
    sql_query  = " SELECT  A.USER_ID,A.TRAINING_YMD,A.WEATHER_CODE,A.HUMIDITY,A.TRAINING_CONTENT,A.TRAINING_HOUR,"
    sql_query += "         A.WEIGHT_BEFORE,A.WEIGHT_AFTER,A.INTAKE_WATER,A.TEMPERATURE "
    sql_query += " FROM    TBL_DATA_TRAINING A"
    sql_query += "       , MST_USER_ID B"
    sql_query += " WHERE   (A.TRAINING_YMD=CURRENT_DATE OR A.TRAINING_YMD=CURRENT_DATE- INTERVAL 1 DAY)"
    sql_query += " AND     B.ID =A.USER_ID "
    sql_query += " AND     (B.ORG_CODE = (SELECT X.ORG_CODE "
    sql_query += "                        FROM MST_USER_ID X "
    sql_query += "                        WHERE X.ID ='{}'".format(userid)
    sql_query += "                        AND   X.PASSWORD ='{}')".format(userpass)
    sql_query += "          OR 'ADM'   = (SELECT X.ORG_CODE "
    sql_query += "                        FROM MST_USER_ID X"
    sql_query += "                        WHERE X.USER_CLASS=0"
    sql_query += "                        AND  X.ID ='{}'".format(userid)
    sql_query += "                        AND  X.PASSWORD ='{}'))".format(userpass)
    
    rtn_query = my_func_sql.sql_run_query(sql_query)

    data_list = []
    for row in rtn_query:
        data_list.append({'day'     :row[1],#日
                          'username':row[0],
                          'tenki'   :row[2],#天気
                          'shitsudo':row[3],
                          'contents':row[4],#トレーニング内容
                          'time'    :row[5],#時間
                          'wb'      :row[6],#運動前体重
                          'wa'      :row[7],#運動後体重
                          'moi'     :row[8],#飲水量
                          'temp'    :row[9]})#湿度
        
    return data_list

def sql_message_send(userid,
                     userpass,
                     group,
                     title,
                     contents):

    user_dic=get_user_dic()
    
    if userpass==user_dic[userid]:
        user_dic=get_user_dic()
        
        sql_query  = " INSERT INTO TBL_MESSAGE "
        sql_query += " (MESSAGE_ID, FROM_USER_ID, TO_ORG_CODE, TITLE, CONTENT, ADD_YMD, ADD_TIME, ADD_USER_ID)"
        sql_query += " SELECT CASE WHEN MAX(A.MESSAGE_ID) IS NULL "
        sql_query += "             THEN 1 ELSE MAX(A.MESSAGE_ID) + 1"
        sql_query += "             END,"
        sql_query += "        '{}','{}','{}','{}', CURRENT_DATE(),CURRENT_TIME(),'{}'"
        sql_query += " FROM TBL_MESSAGE A"

        sql_query = sql_query.format(userid,group,title,contents,userid)
        print(sql_query)
        rtn_query = my_func_sql.sql_update_query(sql_query)
        
        return  'OK'
    return 'Not found'

def sql_message_get(userid,userpass, max_messages = 10):
    data_list = []

    sql_query  = " SELECT A.ADD_YMD,A.TO_USER_ID,A.TO_ORG_CODE,A.TITLE,A.CONTENT,B.NAME"
    sql_query += " FROM    TBL_MESSAGE A"
    sql_query += "        ,MST_USER_ID B"
    sql_query += " WHERE (   A.TO_ORG_CODE = 'ALL' "
    sql_query += "        OR A.TO_ORG_CODE = (SELECT X.ORG_CODE"
    sql_query += "                            FROM MST_USER_ID X"
    sql_query += "                            WHERE X.ID ='{}'".format(userid)
    sql_query += "                            AND   X.PASSWORD ='{}'))".format(userpass)
    sql_query += " AND     B.ID=A.FROM_USER_ID"
    sql_query += " ORDER BY A.ADD_YMD DESC"
    rtn_query = my_func_sql.sql_run_query(sql_query)
    
    for row in rtn_query:
        data_list.append({
            'day'     : row[0],#日
            'userid'  : row[1],
            'group'   : row[2],
            'title'   : row[3],
            'contents': row[4],
            'rname'   : row[5]
        })
    
    if len(data_list) > max_messages:
        return data_list[:max_messages]
    return data_list    

# 一般ユーザーによるユーザーの追加
def adduser_general(info):
    # user_dic = get_user_dic()
    # if adminpass == user_dic[admin]:
    sql_query  = " INSERT INTO MST_USER_ID"
    sql_query += "  (ID, PASSWORD,USER_CLASS,ORG_CODE,NAME,ENTRY_YEAR,MAIL_ADDRESS,ACTIVE_VALUE,TEMP_REGISTRATION_ID,"
    sql_query += "   ADD_YMD, ADD_TIME, ADD_USER_ID) "
    sql_query += " VALUES ('{}','{}','{}','{}','{}','{}','{}',2,'{}',CURRENT_DATE,CURRENT_TIME,'{}')".format(info['newuser'],info['newpass'],info['type'],info['org'],info['rname'],info['year'],info['mail'],randomname(20),info['newuser'])
    rtn_query = my_func_sql.sql_update_query(sql_query)
        
    return  'OK'

# 管理者によるユーザーの追加
def adduser(admin, adminpass, info):
    user_dic = get_user_dic()
    if adminpass == user_dic[admin]:
        sql_query = '''INSERT INTO MST_USER_ID 
                        (ID, PASSWORD, NAME, ORG_CODE, USER_CLASS, ENTRY_YEAR, ACTIVE_VALUE, MAIL_ADDRESS, ADD_YMD, ADD_TIME, ADD_USER_ID,TEMP_REGISTRATION_ID)
                    VALUES ('{}','{}','{}','{}','{}','{}',1,NULL,CURRENT_DATE,CURRENT_TIME,'{}','{}')'''.format(info['newuser'],info['newpass'],info['rname'],info['org'], info['type'],info['year'],admin,info['newuser'])
        rtn_query = my_func_sql.sql_update_query(sql_query)
        
        return  'OK'
    return 'NG'

def addorg(admin, adminpass, info):
    user_dic = get_user_dic()
    if adminpass == user_dic[admin]:
        sql_query = '''INSERT INTO MST_ORG (ORG_CODE,ORG_NAME,ADD_YMD,ADD_TIME,ADD_USER_ID) 
                    VALUES ('{}','{}',CURRENT_DATE,CURRENT_TIME,'{}')'''.format(info['org_id'], info['org_name'],admin)
        rtn_query = my_func_sql.sql_update_query(sql_query)
        
        return  True
    return False

def update_user(admin, adminpass, user, op):
    user_dic = get_user_dic()
    if adminpass == user_dic[admin]:
        
        if op == 'stop':
            i = -1
        elif op == 'user':
            i = 1
        elif op == 'admin':
            i = 0
        elif op == 'coach':
            i = 2
        
        sql_query = '''UPDATE `user_list` SET `type` = {} WHERE `id` = '{}';
                   '''.format(i, user)
        rtn_query = my_func_sql.sql_update_query(sql_query)
        
        return  'OK'
    return 'NG'

def sql_data_per_day(day):
    #user_name ←のアカウントを使って
    #user_nm ←のデータを取得
    sql_query  = " SELECT USER_ID, TRAINING_YMD, WEATHER_CODE, HUMIDITY, TRAINING_CONTENT, TRAINING_HOUR,"
    sql_query += "        WEIGHT_BEFORE, WEIGHT_BEFORE, INTAKE_WATER, TEMPERATURE"
    sql_query += " FROM   TBL_DATA_TRAINING"
    sql_query += " WHERE  TRAINING_YMD='{}'".format(day)
    rtn_query = my_func_sql.sql_run_query(sql_query)
    data_list = []
    for row in sql_query:
        data_list.append({'day'     :row[1],#日
                          'tenki'   :row[2],#天気
                          'shitsudo':row[3],
                          'contents':row[4],#トレーニング内容
                          'time'    :row[5],#時間
                          'wb'      :row[6],#運動前体重
                          'wa'      :row[7],#運動後体重
                          'moi'     :row[8],#飲水量
                          'temp'    :row[9]})#湿度
    
    return data_list


def add_entry_tmp_account_mail(info,org_dic):
    mail_content = ""
    mail_title   = ""

    sql_query  = " SELECT VAL1"
    sql_query += " FROM   MST_KBN_CODE"
    sql_query += " WHERE  CLASS_CODE='MAIL_TITLE'"
    sql_query += " AND    CODE='1'"
    rtn_query  = my_func_sql.sql_run_query(sql_query)
    mail_title +=rtn_query[0][0]

    mail_content += "{rname}さん\n\n".format(rname=info['rname'])
    sql_query  = " SELECT VAL2"
    sql_query += " FROM   MST_KBN_CODE"
    sql_query += " WHERE  CLASS_CODE='MAIL_CONTENT'"
    sql_query += " AND    CODE='KH'"
    rtn_query  = my_func_sql.sql_run_query(sql_query)
    mail_content +=rtn_query[0][0]

    sql_query  = " SELECT TEMP_REGISTRATION_ID"
    sql_query += " FROM   MST_USER_ID"
    sql_query += " WHERE  ID='{newuser}'".format(newuser=info['newuser'])
    sql_query += " AND    ACTIVE_VALUE=2"
    rtn_query  = my_func_sql.sql_run_query(sql_query)
    mail_content+=server_address+"/newaccount?resgs=hon&userid={userid}&tmpregisid={tmpregisid}".format(userid=info['newuser'],tmpregisid=rtn_query[0][0])

    mail_content += '\n    【登録情報】\n'\
           +'\tユーザー名：{newuser}\n'\
           +'\t名前：{rname}\n'\
           +'\t組織：{org_name}\n'\
           +'\t入学年度：{year}\n'\
           +'\n\n'
     
    mail_content=mail_content.format(newuser=info['newuser'],
                            rname=info['rname'],
                            org_name=org_dic[info['org']]['org_name'],
                            year=info['year'])

    sql_query  = " SELECT VAL2"
    sql_query += " FROM   MST_KBN_CODE"
    sql_query += " WHERE  CLASS_CODE='MAIL_CONTENT'"
    sql_query += " AND    CODE='KF'"
    rtn_query  = my_func_sql.sql_run_query(sql_query)
    mail_content +=rtn_query[0][0]

    sql_query  = " INSERT INTO TBL_MAIL"
    sql_query += "  (MAIL_ID, MAIL_TO, MAIL_CC, TITLE, CONTENT, FLG_SEND, ADD_YMD, ADD_TIME, ADD_USER_ID) "
    sql_query += " SELECT CASE WHEN MAX(MAIL_ID) IS NULL THEN 1 ELSE MAX(MAIL_ID)+1 END,"
    sql_query += "   '{}','','{}','{}',0, CURRENT_DATE(),CURRENT_TIME(),'sys' FROM TBL_MAIL  ".format(info['mail'],mail_title,mail_content)

    rtn_query = my_func_sql.sql_update_query(sql_query)

    return 'ok'

def add_entry_complete_account_mail(userid,tmpregisid):
    mail_content = ""
    mail_title   = ""
    rname = ""
    mail_address = ""

    sql_query  = " SELECT NAME, MAIL_ADDRESS"
    sql_query += " FROM   MST_USER_ID"
    sql_query += " WHERE  ID='{userid}'".format(userid=userid)
    sql_query += " AND    ACTIVE_VALUE=2"
    sql_query += " AND    TEMP_REGISTRATION_ID='{tmpregisid}'".format(tmpregisid=tmpregisid)
    rtn_query  = my_func_sql.sql_run_query(sql_query)
    if rtn_query == []:
        return 1

    rname =rtn_query[0][0]
    mail_address =rtn_query[0][1]

    sql_query  = " SELECT VAL1"
    sql_query += " FROM   MST_KBN_CODE"
    sql_query += " WHERE  CLASS_CODE='MAIL_TITLE'"
    sql_query += " AND    CODE='2'"
    rtn_query  = my_func_sql.sql_run_query(sql_query)
    mail_title +=rtn_query[0][0]

    mail_content += "{rname}さん\n\n".format(rname=rname)
    sql_query  = " SELECT VAL2"
    sql_query += " FROM   MST_KBN_CODE"
    sql_query += " WHERE  CLASS_CODE='MAIL_CONTENT'"
    sql_query += " AND    CODE='HH'"
    rtn_query  = my_func_sql.sql_run_query(sql_query)
    mail_content +=rtn_query[0][0]

    mail_content += server_address+'\n'

    sql_query  = " SELECT VAL2"
    sql_query += " FROM   MST_KBN_CODE"
    sql_query += " WHERE  CLASS_CODE='MAIL_CONTENT'"
    sql_query += " AND    CODE='HF'"
    rtn_query  = my_func_sql.sql_run_query(sql_query)
    mail_content +=rtn_query[0][0]

    sql_query  = " INSERT INTO TBL_MAIL"
    sql_query += "  (MAIL_ID, MAIL_TO, MAIL_CC, TITLE, CONTENT, FLG_SEND, ADD_YMD, ADD_TIME, ADD_USER_ID) "
    sql_query += " SELECT CASE WHEN MAX(MAIL_ID) IS NULL THEN 1 ELSE MAX(MAIL_ID)+1 END,"
    sql_query += "   '{}','','{}','{}',0, CURRENT_DATE(),CURRENT_TIME(),'sys' FROM TBL_MAIL  ".format(mail_address,mail_title,mail_content)
    rtn_query = my_func_sql.sql_update_query(sql_query)

    sql_query  = " UPDATE MST_USER_ID"
    sql_query += " SET    ACTIVE_VALUE = 1 "
    sql_query += "      , UPD_YMD = CURRENT_DATE"
    sql_query += "      , UPD_TIME = CURRENT_TIME"
    sql_query += "      , UPD_USER_ID = '{userid}'".format(userid=userid)
    sql_query += " WHERE  ID  = '{userid}'".format(userid=userid)
    sql_query += " AND    ACTIVE_VALUE = 2"
    rtn_query = my_func_sql.sql_update_query(sql_query)

    return 0

def sql_makecsv(file, name, userid,userpass):
    data_list = []
    
    if file == "data":
        sql_query  = " SELECT A.USER_ID,A.TRAINING_YMD, A.WEATHER_CODE, A.HUMIDITY, A.TRAINING_CONTENT,A.TRAINING_HOUR,"
        sql_query += "        A.WEIGHT_BEFORE,A.WEIGHT_AFTER,A.INTAKE_WATER,A.TEMPERATURE, B.NAME"
        sql_query += " FROM   TBL_DATA_TRAINING A"
        sql_query += "       ,MST_USER_ID B"
        sql_query += " WHERE  A.USER_ID = B.ID"
        sql_query += " AND    (B.ORG_CODE   = (SELECT X.ORG_CODE "
        sql_query += "                         FROM MST_USER_ID X"
        sql_query += "                         WHERE X.ID = '{}'".format(userid)
        sql_query += "                         AND   X.PASSWORD = '{}')".format(userpass)
        sql_query += "                         AND   (X.USER_CLASS = 0 "
        sql_query += "                                OR X.USER_CLASS = 2)"
        sql_query += "         OR 'ADM'     = (SELECT X.ORG_CODE "
        sql_query += "                         FROM MST_USER_ID X "
        sql_query += "                         WHERE X.ID = '{}'".format(userid)
        sql_query += "                         AND   X.PASSWORD = '{}'".format(userpass)
        sql_query += "                         AND   X.USER_CLASS = 0))"
        if name is not None:
            sql_query += " AND    A.USER_ID = '{}'".format(name)
            filename = "data_{}.csv".format(name)
        else:
            filename = "data_ALL.csv"

        rtn_query = my_func_sql.sql_run_query(sql_query)
        for row in rtn_query:
            data_list.append({'USER_ID'      :row[10],
                              'TRAINING_YMD'     :row[1],#日
                              'WEATHER_CODE' :row[2],#天気
                              'HUMIDITY':" " if row[3] == 1111 else row[3],
                              'TRAINING_CONTENT':row[4],#トレーニング内容
                              'TRAINING_HOUR'    :row[5],#時間
                              'WEIGHT_BEFORE' :row[6],#運動前体重
                              'WEIGHT_AFTER' :row[7],#運動後体重
                              'INTAKE_WATER'   :row[8],#飲水量
                              'TEMPERATURE'    :" " if row[9] == 1111 else row[9]})
        
        with open(filename, 'w', newline = "", encoding='shift-jis' ) as csv_file:
            fieldnames = ['USER_ID', 'TRAINING_YMD', 'WEATHER_CODE', 'HUMIDITY', 'TRAINING_CONTENT',
                          'TRAINING_HOUR', 'WEIGHT_BEFORE', 'WEIGHT_AFTER', 'INTAKE_WATER', 'TEMPERATURE']
            writer = csv.DictWriter(csv_file, 
                                    fieldnames = fieldnames)
            writer.writeheader()
            for d in data_list:
                writer.writerow(d)
        return True
    
    elif file == "user":
        sql_query  = " SELECT A.ID, A.USER_CLASS, A.NAME, A.ORG_CODE, A.ENTRY_YEAR, B.VAL1 AS USER_CLASS_NAME,C.ORG_NAME "
        sql_query += " FROM  MST_USER_ID A "
        sql_query += "      ,MST_KBN_CODE B"
        sql_query += "      ,MST_ORG C"
        sql_query += " WHERE "
        sql_query += "        (A.ORG_CODE   = (SELECT X.ORG_CODE "
        sql_query += "                         FROM MST_USER_ID X"
        sql_query += "                         WHERE X.ID = '{}'".format(userid)
        sql_query += "                         AND   X.PASSWORD = '{}')".format(userpass)
        sql_query += "         OR 'ADM'     = (SELECT X.ORG_CODE "
        sql_query += "                         FROM MST_USER_ID X "
        sql_query += "                         WHERE X.ID = '{}'".format(userid)
        sql_query += "                         AND   X.PASSWORD = '{}'".format(userpass)
        sql_query += "                         AND   X.USER_CLASS = 0))"

        sql_query += " AND B.CLASS_CODE = 'USER_CLASS'"
        sql_query += " AND B.CODE = A.USER_CLASS"
        sql_query += " AND C.ORG_CODE = A.ORG_CODE"
        sql_query += " "

        rtn_query = my_func_sql.sql_run_query(sql_query)
        for row in rtn_query:
            data_list.append({
                     'ID'   :row[0],
                     'rname':row[2],
                     'type' :row[5],
                     'org'  :row[6],
                     'year' :row[4]
                     })

        with open('user_list.csv', 'w', newline = "", encoding='shift-jis') as csv_file:
            fieldnames = ['ID', 'rname', 'type', 'org', 'year']
            writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
            writer.writeheader()
            for d in data_list:
                writer.writerow(d)
        return True
    return False

def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

# --Written By Mutsuyo-----------------------------------
def dassui_ritu(wb, wa):#脱水率
    z = round((wa - wb) / wb * 100, 1)#wb運動前　wa運動後
    return z

def hakkann_ritu(wb, wa, water, time):#1時間あたり発汗量
    z = round((wb - wa + water)/time, 2)#water運動中飲水量?　#time運動時間
    return z

def hakkann_ryo(wb, wa, water):#運動中発汗量(飲水必要量)
    z = round(wb - wa + water, 2)
    return z

def hakkann_ritu_ex1(wb, water, time):#1時間あたり-1%発汗量
    z = round((wb - wb * 0.99 + water) / time, 2)#water運動中飲水量?　#time運動時間
    return z

def hakkann_ryo_ex1(wb,water):#運動時間あたり-1%発汗量(飲水必要量)
    z = round(wb-wb*0.99+water,2)#water運動中飲水量?　#time運動時間
    return z
# -------------------------------------------------------

def generateComment(data):
    sentence = 'おつかれさま。'
    if 0 <= data['dehydraterate']:
        sentence += 'トレーニング中水分補給がんばった!!'
        img = 'suzuki1.jpg'
    elif -1.0 < data['dehydraterate'] < 0:
        sentence += 'トレーニング中の水分補給大事。この調子!!'
        img = 'suzuki2.jpg'
    elif -2.0 <= data['dehydraterate'] <= -1.0:
    #elif -1.0 < data['dehydraterate']:
        sentence += '水分補給もう少し。目指せ脱水率-1%以内でパフォーマンスup!'
        img = 'suzuki3.jpg'
    elif data['dehydraterate'] < -2.0:
        sentence += '''トレーニング中水分不足だよ。水分補給を増やして、
                    熱中症や食欲不振を予防しよう。目指せ脱水率-1%以内。
                    '''
        img = 'suzuki4.jpg'
    else:
        img = 'suzuki1.jpg'
        sentence = 'ERROR'
    return {'sentence':sentence,
            'img'     :img}