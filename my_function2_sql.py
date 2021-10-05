# -*- coding: utf-8 -*-
"""
Created on Fri May 17 12:52:30 2019

@author: Azumi Mamiya
         Daiki Miyagawa

version: v1.1
"""

import mysql.connector
import datetime
import csv
import configparser

config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

# SQLserver_host = '192.168.0.32'
# SQLserver_host = '192.168.0.32'

SQLserver_host = config_ini['DEFAULT']['SQLserver_host']
SQLserver_port = config_ini['DEFAULT']['SQLserver_port']
database_name = config_ini['DEFAULT']['database_name']
sql_userid = config_ini['DEFAULT']['sql_userid']
sql_userpass = config_ini['DEFAULT']['sql_userpass']

# すべてのユーザーのIDとパスを表示，my_function内のみ使用
def get_user_dic():
    user_dic = {}
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
    cur.execute('''SELECT `{}`,`{}` FROM `{}` '''
                .format("id", "password", "user_list"))
    for row in cur.fetchall():
        user_dic[row[0]] = row[1]
    return user_dic

# 全てのユーザーの全ての情報を取得，my_function内のみ使用
def get_user_info():
    user_info = []
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
    cur.execute('''SELECT * FROM `{}` '''.format("user_list"))
    for row in cur.fetchall():
        user_info.append({'id'       : row[0],
                          'password' : row[1],
                          'type'     : str(row[2]),
                          'rname'    : row[3],
                          'org'      : row[4],
                          'year'     : row[5]})
    cur.close()
    conn.close()
    return user_info

def sql_ALLuser_profile():
    # kakunin(user_name, user_pass)
    user_prof = {}
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
    cur.execute('''SELECT `{}`,`{}`,`{}`,`{}`,`{}` FROM `{}` '''
                .format("id","type","rname","org","year","user_list"))
    for row in cur.fetchall():
        user_prof[row[0]] = {
                 'rname':row[2],
                 'type' :row[1],
                 'org'  :row[3],
                 'year' :row[4]
                 }
    
    return user_prof

# 組織リスト取得
def get_org():
    # kakunin(user_name, user_pass)
    org_dic = {}
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
    cur.execute('''SELECT `{}`,`{}` FROM `{}` '''
                .format("org_id","org_name","org_list"))
    for row in cur.fetchall():
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
                and user_info[i]['type'] == '0':
            connected = True
            break
    return connected

def admin_coach_kakunin(user_name, user_pass):
    connected = False
    user_info = get_user_info()
    for i in range(len(user_info)):
        if user_name == user_info[i]['id'] \
            and user_pass == user_info[i]['password'] \
                and user_info[i]['type'] == '0' or '2':
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
        Rtime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")\
                 + user_name
        tmp_day = datetime.date.today()
        day = tmp_day.strftime('%Y-%m-%d')
        cur.execute(
                '''INSERT INTO `{}` (`id`,`day`, `weather`, `humidity`, 
                `training`,`time`, `bweight`,`aweight`,`water`,`temp`,`rtime`) 
                    VALUES ('{}', '{}', {}, {},'{}',{},{},{},{},{},'{}')
                '''.format('data', user_name, day, weather, humidity,
                            training, time, bweight, aweight, water,
                            temp, Rtime)
                    )
        
        conn.commit()
        cur.close()
        conn.close()
        
        return  'OK'
    return  'NG'

def sql_data_get(user_nm):
    #user_name ←のアカウントを使って
    #user_nm ←のデータを取得
    data_list = []
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
    cur.execute('''SELECT `id`,`day`, `weather`, `humidity`, `training`,`time`,
                    `bweight`,`aweight`,`water`,`temp` FROM `{}` WHERE id = '{}' 
                '''.format("data", user_nm))
    
    for row in cur.fetchall():
        data_list.append({'day'     :row[1],#日
                          'tenki'   :row[2],#天気
                          'shitsudo':row[3],
                          'contents':row[4],#トレーニング内容
                          'time'    :row[5],#時間
                          'wb'      :row[6],#運動前体重
                          'wa'      :row[7],#運動後体重
                          'moi'     :row[8],#飲水量
                          'temp'    :row[9]})#湿度
    cur.close()
    conn.close()
    data_list.sort(key = lambda x:x['day'])
    
    return data_list

def sql_data_get_latest_all(i, org):
    today = datetime.date.today().strftime('%Y-%m-%d')
    yesterday = (datetime.date.today()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    data_list = []
    # user_dic = get_user_dic()
    #for u_name in user_dic.keys():
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
    
    if i == 0:    
        sentence = '''SELECT `id`,`day`, `weather`, `humidity`, `training`,`time`,
                      `bweight`,`aweight`,`water`,`temp` FROM `{}` WHERE day='{}'or day='{}';
                    '''.format("data",today,yesterday)
    else:
        dic = sql_ALLuser_profile()
        user_list = [user for user in dic.keys() if org == dic[user]['org']]
        cond = '('
        for id in user_list:
            cond += "id = '{}' or ".format(id)
        cond = cond[:-3] + ')'
        
        sentence = '''SELECT `id`,`day`, `weather`, `humidity`, `training`,`time`,
                      `bweight`,`aweight`,`water`,`temp` FROM `{}` WHERE (day='{}'or day='{}') and {};
                    '''.format("data", today, yesterday, cond)
    
    cur.execute(sentence)
    data_list = []
    for row in cur.fetchall():
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
    cur.close()
    conn.close()
        
    return data_list

def sql_message_send(userid,
                     userpass,
                     group,
                     title,
                     contents):

    user_dic=get_user_dic()
    
    if userpass==user_dic[userid]:
        user_dic=get_user_dic()
        
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
        Rtime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")\
                 + userid
        tmp_day=datetime.date.today()
        day=tmp_day.strftime('%Y-%m-%d')
        cur.execute('''INSERT INTO `{}` (`day`,`tolist`, `fromlist`, `title`, `contents`, `rtime`) 
                    VALUES ('{}','{}','{}','{}','{}', '{}')'''
                    .format('board',day,group,userid,title,contents,Rtime))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return  'OK'
    return 'Not found'

def sql_message_get(userid, userpass, max_messages = 10):
    
    user_dic=get_user_dic()
    data_list = []
    if userpass==user_dic[userid]:
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
        cur.execute('''SELECT `{}`,`{}`,`{}`,`{}`,`{}` FROM `{}` '''
                    .format("day","tolist","fromlist","title","contents","board"))
        for row in cur.fetchall():
            data_list.append({
                'day'     : row[0],#日
                'userid'  : row[2],
                'group'   : row[1],
                'title'   : row[3],
                'contents': row[4],
            })
            data_list.sort(key=lambda x:x['day'])
            data_list.reverse()
    
    if len(data_list) > max_messages:
        return data_list[:max_messages]
    return data_list    

# 一般ユーザーによるユーザーの追加
def adduser_general(info):
    # user_dic = get_user_dic()
    # if adminpass == user_dic[admin]:
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
    cur.execute('''INSERT INTO `{}` (`id`,`password`, `type`,`org`,`rname`, `year`, `mail`) 
                VALUES ('{}','{}','{}','{}','{}','{}','{}')'''
                .format('user_list',info['newuser'],info['newpass'],info['type'],info['org'],info['rname'],info['year'],info['mail']))
        
    conn.commit()
    cur.close()
    conn.close()
        
    return  'OK'

# 管理者によるユーザーの追加
def adduser(admin, adminpass, info):
    user_dic = get_user_dic()
    if adminpass == user_dic[admin]:
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
        cur.execute('''INSERT INTO `{}` (`id`,`password`, `type`,`org`,`rname`, `year`) 
                    VALUES ('{}','{}','{}','{}','{}','{}')'''
                    .format('user_list',info['newuser'],info['newpass'],info['type'],info['org'],info['rname'],info['year']))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return  'OK'
    return 'NG'

def addorg(admin, adminpass, info):
    user_dic = get_user_dic()
    if adminpass == user_dic[admin]:
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
        cur.execute('''INSERT INTO `{}` (`org_id`,`org_name`) 
                    VALUES ('{}','{}')'''
                    .format('org_list', info['org_id'], info['org_name']))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return  True
    return False

def update_user(admin, adminpass, user, op):
    user_dic = get_user_dic()
    if adminpass == user_dic[admin]:
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
        
        if op == 'stop':
            i = -1
        elif op == 'user':
            i = 1
        elif op == 'admin':
            i = 0
        elif op == 'coach':
            i = 2
        
        sentence = '''UPDATE `user_list` SET `type` = {} WHERE `id` = '{}';
                   '''.format(i, user)
        #UPDATE `dehydration2`.`user_list` SET `type` = '0' WHERE `user_list`.`id` = 'tomohiro';
        
        cur.execute(sentence)
        
        conn.commit()
        cur.close()
        conn.close()
        
        return  'OK'
    return 'NG'

def sql_data_per_day(day):
    #user_name ←のアカウントを使って
    #user_nm ←のデータを取得
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
    cur.execute('''SELECT `id`,`day`, `weather`, `humidity`, `training`,`time`,
                    `bweight`,`aweight`,`water`,`temp` FROM `{}` WHERE day='{}';
                '''.format("data",day))
    data_list = []
    for row in cur.fetchall():
        data_list.append({'day'     :row[1],#日
                          'tenki'   :row[2],#天気
                          'shitsudo':row[3],
                          'contents':row[4],#トレーニング内容
                          'time'    :row[5],#時間
                          'wb'      :row[6],#運動前体重
                          'wa'      :row[7],#運動後体重
                          'moi'     :row[8],#飲水量
                          'temp'    :row[9]})#湿度
    cur.close()
    conn.close()
    
    return data_list

def sql_makecsv(file, name):
    data_list = []
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
    if file == "data":
        if name == None:
            sentence = '''SELECT `id`,`day`, `weather`, `humidity`, `training`,`time`,
                            `bweight`,`aweight`,`water`,`temp`,`rtime` FROM `{}`'''\
                            .format("data")
            filename = "data_ALL.csv"
        else:
            sentence = '''SELECT `id`,`day`, `weather`, `humidity`, `training`,`time`,
                            `bweight`,`aweight`,`water`,`temp`,`rtime` FROM `{}` WHERE id='{}' ''' \
                            .format("data", name)
            filename = "data_{}.csv".format(name)
        
        cur.execute(sentence)
        user_prof = sql_ALLuser_profile()
        for row in cur.fetchall():
            data_list.append({'id'      :user_prof[row[0]]['rname'],
                              'day'     :row[1],#日
                              'weather' :row[2],#天気
                              'humidity':" " if row[3] == 1111 else row[3],
                              'training':row[4],#トレーニング内容
                              'time'    :row[5],#時間
                              'bweight' :row[6],#運動前体重
                              'aweight' :row[7],#運動後体重
                              'water'   :row[8],#飲水量
                              'temp'    :" " if row[9] == 1111 else row[9]})
        cur.close()
        conn.close()
        
        with open(filename, 'w', newline = "", encoding='shift-jis' ) as csv_file:
            fieldnames = ['id', 'day', 'weather', 'humidity', 'training',
                          'time', 'bweight', 'aweight', 'water', 'temp', 'rtime']
            writer = csv.DictWriter(csv_file, 
                                    fieldnames = fieldnames)
            writer.writeheader()
            for d in data_list:
                writer.writerow(d)
        return True
    
    elif file == "user":
        cur.execute('''SELECT `{}`,`{}`,`{}`,`{}`,`{}` FROM `{}` '''
                .format("id","type","rname","org","year","user_list"))
        for row in cur.fetchall():
            data_list.append({
                     'id'   :row[0],
                     'rname':row[2],
                     'type' :row[1],
                     'org'  :row[3],
                     'year' :row[4]
                     })

        cur.close()
        with open('user_list.csv', 'w', newline = "", encoding='shift-jis') as csv_file:
            fieldnames = ['id', 'password', 'type', 'rname', 'org', 'year']
            writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
            writer.writeheader()
            for d in data_list:
                writer.writerow(d)
        return True
    return False
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
    return {
            'sentence':sentence,
            'img'     :img
            }