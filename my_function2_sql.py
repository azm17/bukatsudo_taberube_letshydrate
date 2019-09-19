# -*- coding: utf-8 -*-
"""
Created on Fri May 17 12:52:30 2019

@author: Azumi Mamiya
         Daiki Miyagawa
"""

import mysql.connector
import datetime
import csv

SQLserver_host='192.168.0.32'
SQLserver_port=3306
database_name='dehydration2'
sql_userid='mutsu624'
sql_userpass='624mutsu'

#my_function内のみ使用
#すべてのユーザーのIDとパスを表示
def get_user_dic():
    user_dic={}
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
    cur.execute('''SELECT `{}`,`{}` FROM `{}` '''.format("id","password","user_list"))
    for row in cur.fetchall():
        user_dic[row[0]]=row[1]
    return user_dic

#my_function内のみ使用
def get_user_info():
    user_info=[]
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
        user_info.append({'id':row[0],
                          'password':row[1],
                          'type':str(row[2]),
                          'rname':row[3],
                          'org':row[4],
                          'year':row[5]})
    cur.close()
    conn.close()
    return user_info

def sql_ALLuser_profile(user_name, user_pass):
    kakunin(user_name, user_pass)
    user_prof={}    
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
        user_prof[row[0]]={
                 'rname':row[2],
                 'type':row[1],
                 'org':row[3],
                 'year':row[4]}
    
    return user_prof
#ログイン処理
def kakunin(user_name, user_pass):
    connected=False
    user_dic=get_user_dic()
    if user_name in user_dic.keys():
        if user_pass==user_dic[user_name]:
            connected=True
    return connected

def admin_kakunin(user_name, user_pass):
    connected=False
    user_info=get_user_info()
    for i in range(len(user_info)):
        if user_name==user_info[i]['id'] \
            and user_pass==user_info[i]['password'] \
                and user_info[i]['type']=='0':
            connected=True
            break
    return connected
def get_admin():
    user_info=get_user_info()
    admin=[]
    for i in range(len(user_info)):
        if user_info[i]['type']=='0':
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
    
    user_dic=get_user_dic()
    if user_pass==user_dic[user_name]:
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
        Rtime=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        tmp_day=datetime.date.today()
        day=tmp_day.strftime('%Y-%m-%d')
        cur.execute('''INSERT INTO `{}` (`id`,`day`, `weather`, `humidity`, `training`,`time`,
                    `bweight`,`aweight`,`water`,`temp`,`rtime`) 
                    VALUES ('{}','{}',{},{},'{}',{},{},{},{},{},{})'''
                    .format('data',user_name,day,weather,humidity,training,time,bweight,aweight,water,temp,Rtime))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return  'OK'
    return  'NG'
def sql_data_get(user_nm):
    #user_name ←のアカウントを使って
    #user_nm ←のデータを取得
    data_list=[]
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
                    `bweight`,`aweight`,`water`,`temp` FROM `{}` WHERE id = '{}' '''.format("data",user_nm))
    for row in cur.fetchall():
        data_list.append({'day':row[1],#日
                          'tenki':row[2],#天気
                          'shitsudo':row[3],
                          'contents':row[4],#トレーニング内容
                          'time':row[5],#時間
                          'wb':row[6],#運動前体重
                          'wa':row[7],#運動後体重
                          'moi':row[8],#飲水量
                          'temp':row[9]})#湿度
    cur.close()
    conn.close()
    data_list.sort(key=lambda x:x['day'])
    
    return data_list

def sql_data_get_latest_all():
    today = datetime.date.today().strftime('%Y-%m-%d')
    yesterday=(datetime.date.today()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    data_list=[]
    user_dic=get_user_dic()
    for u_name in user_dic.keys():
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
                        `bweight`,`aweight`,`water`,`temp` FROM `{}` WHERE day='{}'or day='{}'  '''
                        .format("data",today,yesterday))
        data_list=[]
        for row in cur.fetchall():
            data_list.append({'day':row[1],#日
                              'username':row[0],
                              'tenki':row[2],#天気
                              'shitsudo':row[3],
                              'contents':row[4],#トレーニング内容
                              'time':row[5],#時間
                              'wb':row[6],#運動前体重
                              'wa':row[7],#運動後体重
                              'moi':row[8],#飲水量
                              'temp':row[9]})#湿度
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
        tmp_day=datetime.date.today()
        day=tmp_day.strftime('%Y-%m-%d')
        cur.execute('''INSERT INTO `{}` (`day`,`tolist`, `fromlist`, `title`, `contents`) 
                    VALUES ('{}','{}','{}','{}','{}')'''
                    .format('board',day,group,userid,title,contents))
        
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
                'day':row[0],#日
                'userid':row[2],
                'group': row[1],
                'title': row[3],
                'contents': row[4],
            })
            data_list.sort(key=lambda x:x['day'])
            data_list.reverse()
    
    if len(data_list) > max_messages:
        return data_list[:max_messages]
    return data_list    

def adduser(admin,adminpass,info):
    user_dic=get_user_dic()
    if adminpass==user_dic[admin]:
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
                    `bweight`,`aweight`,`water`,`temp` FROM `{}` WHERE day='{}' '''.format("data",day))
    data_list=[]
    for row in cur.fetchall():
        data_list.append({'day':row[1],#日
                          'tenki':row[2],#天気
                          'shitsudo':row[3],
                          'contents':row[4],#トレーニング内容
                          'time':row[5],#時間
                          'wb':row[6],#運動前体重
                          'wa':row[7],#運動後体重
                          'moi':row[8],#飲水量
                          'temp':row[9]})#湿度
    cur.close()
    conn.close()
    
    return data_list

def sql_makecsv(file):
    data_list=[]
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
    if file=="data":
        cur.execute('''SELECT `id`,`day`, `weather`, `humidity`, `training`,`time`,
                        `bweight`,`aweight`,`water`,`temp`,`rtime` FROM `{}`'''.format("data"))
        for row in cur.fetchall():
            data_list.append({'id':row[0],
                              'day':row[1],#日
                              'weather':row[2],#天気
                              'humidity':row[3],
                              'training':row[4],#トレーニング内容
                              'time':row[5],#時間
                              'bweight':row[6],#運動前体重
                              'aweight':row[7],#運動後体重
                              'water':row[8],#飲水量
                              'temp':row[9],
                              'rtime':row[10]})#湿度
        cur.close()
        conn.close()
        
        with open('data.csv', 'w', newline="") as csv_file:
            fieldnames = ['id', 'day','weather','humidity','training','time','bweight','aweight','water','temp','rtime']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for d in data_list:
                writer.writerow(d)
        
    elif file=="user":
        cur.execute('''SELECT `{}`,`{}`,`{}`,`{}`,`{}` FROM `{}` '''
                .format("id","type","rname","org","year","user_list"))
        for row in cur.fetchall():
            data_list.append({
                     'id':row[0],
                     'rname':row[2],
                     'type':row[1],
                     'org':row[3],
                     'year':row[4]})

        cur.close()
        with open('user_list.csv', 'w', newline="") as csv_file:
            fieldnames = ['id','password', 'type','rname','org', 'year']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for d in data_list:
                writer.writerow(d)
        
        
    return True
#--Written By Mutsuyo-----------------------------------
def dassui_ritu(wb,wa):#脱水率
    z=round((wa-wb)/wb*100,1)#wb運動前　wa運動後
    return z

def hakkann_ritu(wb,wa,water,time):#1時間あたり発汗量
    z=round((wb-wa+water)/time,2)#water運動中飲水量?　#time運動時間
    return z

def hakkann_ryo(wb,wa,water):#運動中発汗量(飲水必要量)
    z=round(wb-wa+water,2)
    return z

def hakkann_ritu_ex1(wb,water,time):#1時間あたり-1%発汗量
    z=round((wb-wb*0.99+water)/time,2)#water運動中飲水量?　#time運動時間
    return z

def hakkann_ryo_ex1(wb,water):#運動時間あたり-1%発汗量(飲水必要量)
    z=round(wb-wb*0.99+water,2)#water運動中飲水量?　#time運動時間
    return z

#--Written By Mutsuyo-----------------------------------

def generateComment(data):
    sentence='おつかれさま。'
    if 0<=data['dehydraterate']:
        sentence+='トレーニング中水分補給がんばった!!'
        img='suzuki1.jpg'
    elif -1.0<data['dehydraterate']<0:
        sentence+='トレーニング中の水分補給大事。この調子!!'
        img='suzuki2.jpg'
    elif -2.0<=data['dehydraterate']<=-1.0:
    #elif -1.0 < data['dehydraterate']:
        sentence+='水分補給もう少し。目指せ脱水率-1%以内でパフォーマンスup!'
        img='suzuki3.jpg'
    elif data['dehydraterate']<-2.0:
        sentence+='''トレーニング中水分不足だよ。水分補給を増やして、
                    熱中症や食欲不振を予防しよう。目指せ脱水率-1%以内。'''
        img='suzuki4.jpg'
    else:
        img='suzuki1.jpg'
        sentence='ERROR'
    return {'sentence':sentence,'img':img}