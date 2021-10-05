# -*- coding: utf-8 -*-
"""
部活Do!食べる部 Let's hydrate！ v1.1

History:
    Version1.x:
         v1.0 June 29th, 2019, Started developing
              December 29th, 2019, Launched
         v1.1 December 30th, 2019, Revised
         v1.2 January 28th, 2019, Revised
        
    Version2.x:
         None

@author: Azumi Mamiya, Shizuoka University, (Python, HTML, CSS)
         Daiki Miyagawa, Shizuoka University, (Python, HTML, CSS)
         Kenshin Iwakura, Shizuoka University, (HTML, CSS)

Note:
    pip3 install flask
    pip3 install mysql-connector-python
    pip3 import datetime
"""

from flask import Flask, request, render_template, make_response, redirect
import my_function2_sql as my_func
import datetime
import matplotlib.pyplot as plt
import os
import glob
import subprocess

app = Flask(__name__)
# Server Host
# server_host = '192.168.0.12'
# server_host = '192.168.2.102'
# server_host = '192.168.56.1'
server_host = '192.168.2.100'
# server_host='test-server0701.herokuapp.com'

# Server Port
server_port = 50000
server_address = server_host + ':' + str(server_port)
# server_address = server_host

tenki_dic = {'0':' ',
             '1':'🌞️',
             '2':'☁️',
             '3':'🌧️',
             '4':'❄️',
             '5':'室内',
             '13':'🌞️→🌧️',
             '31':'🌧️→🌞️'}

# send login form for general users
@app.route("/")
@app.route("/admin/")
@app.route("/admin")
def entry():
    index = render_template('index.html',
                            serverhost = server_address)
    
    resp = make_response(index)
    resp.set_cookie('user', '')
    resp.set_cookie('pass', '')
    
    return resp

@app.route("/login", methods = ["POST"])
def login():
    try:
        userid = request.form['user']
        userpass = request.form['pass']
    except:
        userid = request.cookies.get('user')
        userpass = request.cookies.get('pass')
    
    user_prof = my_func.sql_ALLuser_profile()
    # ユーザーのタイプ毎にリダイレクト
    if not (my_func.kakunin(userid, userpass)):# アカウントとパスワードの確認
        sentence = 'IDまたはPASSが違います。正しいパスワードを入力してください。'
        redirect_to_index = render_template('error.html',
                                            sentence = sentence)
    
    elif user_prof[userid]['type'] == -1:# 利用停止中のアカウント
        sentence = 'あなたのアカウントは現在利用できません。'
        redirect_to_index = render_template('error.html',
                                            sentence = sentence)
        
    elif user_prof[userid]['type'] == 0:# 管理者
        redirect_to_index = redirect('/admin/show', code=307)
        
    elif user_prof[userid]['type'] == 1:# 一般ユーザー
        redirect_to_index = redirect('/show', code=307)
        
    elif user_prof[userid]['type'] == 2:# 監督・コーチ
        redirect_to_index = redirect('/admin/show', code=307)
    
    resp = make_response(redirect_to_index)
    resp.set_cookie('user', userid)
    resp.set_cookie('pass', userpass)
    return resp

@app.route("/newaccount",
        methods = ["GET", "POST"])
def newaccount():
    text = ''
    org_dic = my_func.get_org()
    if request.args.get('resgs') == 'user':
        # ユーザーの登録
        info = {'newuser':request.form['newuser'],
                'newpass':request.form['newpass'],
                'rname'  :request.form['rname'],
                'type'   :request.form['type'],
                'org'    :request.form['org'],
                'year'   :request.form['year'],
                'mail'   :request.form['mail']
                }
        
        if len(request.form['newuser']) == 0 or len(request.form['newpass']) == 0 or \
            len(request.form['rname']) == 0 or len(request.form['org']) == 0:
            
            sentence = 'ERROR : Fill in the blank!: すべての空欄を埋めてください。'
            index = render_template('error.html',
                                    sentence = sentence)
            return make_response(index)
        
        if request.form['newuser'] in my_func.sql_ALLuser_profile().keys():
            sentence = '''
                        NG: 新しいユーザーを登録できません。
                        ユーザー名[{}]は使われています。違うユーザー名を指定してください。
                        '''.format(request.form['newuser'])
            index = render_template('error.html',
                                    sentence = sentence)
            return make_response(index)
        
        try:
            if my_func.adduser_general(info):
                text = request.form['rname'] + 'さんを登録しました．'

                try:
                    title = '【部活Do!食べる部 Let\'s hydrate！】新規ユーザー登録完了通知'
                    content = '''部活Do!食べる部 Let\'s hydrate！のご利用ありがとうございます。\n\n
                                新規ユーザーの登録が完了しましたので、登録情報を以下に通知します。\n
                                ユーザー名：{}\n
                                パスワード：{}\n
                                名前：{}\n
                                組織：{}\n
                                入学年度：{}\n
                                メールアドレス：{}\n'''.format(info['newuser'], info['newpass'], info['rname'],org_dic[info['org']]['org_name'],info['year'],info['mail'])
                    cmd = 'echo '+ content +'| mail -s '+ title +' -r info@taberube.jp ' + info['mail']
                    subprocess.run(cmd)
                    print(cmd)
                    text = text + '登録完了メールが送信されました。'
                except Exception as error:
                    text = text + 'メールアドレス入力ミスなどにより、登録完了メールは送信されませんでした。エラー内容：' + error.__str__()
                
                index = render_template('registered.html',
                            text = text,
                            serverhost = server_address,
                            newuser = info['newuser'],
                            newpass = info['newpass'],
                            rname = info['rname'],
                            org = org_dic[info['org']]['org_name'],
                            year = info['year'],
                            mail  = info['mail'])
                resp = make_response(index)
                
                return resp
            else:
                return 'NG'
        except Exception as error:
            return 'Fail: SQL Server Error or mail error' + error.__str__()

    
    user_prof = my_func.sql_ALLuser_profile()
    
    posts = []; posts_admin = [] 
    posts_coach = []; posts_unusable = []
    posts_org = []
    
    for name in user_prof.keys():
        dic = {'name':user_prof[name]['rname'],
                'org':org_dic[user_prof[name]['org']]['org_name'],
                'year':user_prof[name]['year'],
                'id':name,
                'keyword':str(user_prof[name]['year']) \
                     + user_prof[name]['org'] + name,
               }
        
        if user_prof[name]['type'] == 0:
            posts_admin.append(dic)
        elif user_prof[name]['type'] == 1:
            posts.append(dic)
        elif user_prof[name]['type'] == 2:
            posts_coach.append(dic)
        elif user_prof[name]['type'] == -1:
            posts_unusable.append(dic)
    
    
    for p in org_dic.keys():
        dic = {'org_id'  :p,
               'org_name':org_dic[p]['org_name']}
        
        posts_org.append(dic)
        
    posts = reversed(sorted(posts, key = lambda x:x['keyword']))
    
    index = render_template('register.html',
                            text = text,
                            serverhost = server_address,
                            posts = posts,
                            posts_admin = posts_admin,
                            posts_coach = posts_coach,
                            posts_unusable = posts_unusable,
                            posts_org = posts_org,
                            year = datetime.datetime.now().year)
    
    resp = make_response(index)
    
    return resp


# 一般ユーザーの結果（表）画面
@app.route("/show", methods = ["POST"])
def show():
    userid = request.cookies.get('user')
    userpass = request.cookies.get('pass')
    
    user_prof = my_func.sql_ALLuser_profile()
    
    if not (my_func.kakunin(userid, userpass)):
        sentence = 'IDまたはPASSが違います。正しいパスワードを入力してください。'
        return make_response(render_template('error.html',
                                         sentence = sentence))
    
    try:
        data = my_func.sql_data_get(userid)
        posts = []
        for d in reversed(data):
            neccessary1_tmp \
                = round(float(d['wb'] * 0.01) + float(d['moi']), 1)
            
            if neccessary1_tmp <= 0:
                neccessary1_tmp = 0
            
            shitsudo = d['shitsudo']
            temp = d['temp']
            if int(shitsudo) == 1111:
                shitsudo = '??'
            if int(temp) == 1111:
                temp = '??'
            posts.append({
                  'date'         :d['day'],# 日
                  'bweight'      :d['wb'],# 運動前体重
                  'aweight'      :d['wa'],# 運動後体重
                  'training'     :d['contents'][0:10],# トレーニング内容
                  'period'       :d['time'],# 運動時間
                  'intake'       :d['moi'],# 飲水量
                  'dehydraterate':my_func.dassui_ritu(d['wb'], d['wa']),# 脱水率
                  'tenki'        :str(tenki_dic[str(d['tenki'])]),# 天気
                  'shitsudo'     :shitsudo,# 湿度
                  'temp'         :temp,# 気温
                  'dassui1'      :round(my_func.hakkann_ritu_ex1(d['wb'], d['wa'], d['time']), 1),
                  'necessary'    :round(my_func.hakkann_ryo(d['wb'], d['wa'], d['moi']), 1),
                  'necessary1'   :neccessary1_tmp,
                  'w1'           :round(d['wb'] * 0.99, 1)
                })
        if len(posts) > 0:
            latest = posts.pop(0)
            data = my_func.generateComment(latest)
            comment = data['sentence']
            img = data['img']
            
        else:
            latest = {
                  'date'         :'今回',   #日
                  'bweight'      :'No data',# 運動前体重
                  'aweight'      :'No data',# 運動後体重
                  'training'     :'No data',# トレーニング内容
                  'period'       :'No data',# 運動時間
                  'intake'       :'No data',# 飲水量
                  'dehydraterate':'No data',# 脱水率
                  # 'dehydrateval' :'No data',# 脱水量
                  'tenki'        :'No data',# 天気
                  'shitsudo'     :'No data',# 湿度
                  'temp'         :'No data',
                  'dassui1'      :'No data',
                  'necessary'    :'No data',
                  'necessary1'   :'No data',
                  'w1'           :'No data'}
            
            comment = '''初めまして。このアプリでは、
                     日々のトレーニング後の脱水量を記録していきます。
                     最初のデータを入力しましょう。
                     下の「データ入力」ボタンから結果を登録できます。
                     また、「アスリートのみなさんへ」は、
                     このアプリを利用している全員向けのコメントです。
                     '''
            
            img = 'suzuki1.png'
        messages = my_func.sql_message_get(
                 userid,
                 userpass,
                 max_messages = 3)
        
        texts = []
        for d in messages:
            texts.append({
                'day'     :d['day'],
                'rname'   :user_prof[d['userid']]['rname'],
                'group'   :d['group'],
                'title'   :d['title'],
                'contents':d['contents']
                }
            )
        
        resp = make_response(render_template('main.html',
                                             title = 'taberube.jp',
                                             user = userid,
                                             posts = posts,
                                             latest = latest,
                                             comment = comment,
                                             texts = texts,
                                             img = img,
                                             rname = user_prof[userid]['rname'],
                                             serverhost = server_address))
        resp.set_cookie('user', userid)
        resp.set_cookie('pass', userpass)
        
        return resp
    except Exception as error:
        sentence = '''
            エラー: 結果の画面が取得できません。
            SQLサーバーが停止している、または、
            表データに不正な文字が含まれているため表示できません。 
            サーバー側に問題があるので、管理者にお問い合わせください。
            (detail:'''+error.__str__()+')'
        return make_response(render_template('error.html',
                                             sentence=sentence))

# Send entry form for data
@app.route("/hello", methods = ["GET","POST"])
def hello():
    userid = request.cookies.get('user')
    userpass = request.cookies.get('pass')
    hantei = my_func.kakunin(userid,userpass)
    user_prof = my_func.sql_ALLuser_profile()
    
    if hantei:# lonin success
        # 11~3月のみ雪マークを追加
        weather = [{'num' : '{}'.format(i),
                    'moji' : tenki_dic[i]}
                     for i in tenki_dic.keys()
                         #if not(4 <= datetime.datetime.today().month <= 10) 
                         #    and i=='4' or i=='0' or i=='1' or i=='2' or i=='3'
                             ]
        # 飲水量の選択肢を追加
        water = ['{:.2f}'.format(round(i*0.05,2))\
                     for i in range(201)]
        
        return render_template('hello.html', 
                               title = 'taberube.jp', 
                               name = user_prof[userid]['rname'],
                               weather = weather,
                               water = water,
                               serverhost = server_address)
    else:# login fail
        sentence = '''You cannot log in on the website. 
                    Please try again from the start! 
                    (最初からやり直してください)'''
        return make_response(render_template('error.html',
                                             sentence = sentence))

# Send data to sql server
@app.route("/enter", methods=["GET","POST"])
def enter():
    userid = request.cookies.get('user')
    userpass = request.cookies.get('pass')
    
    if my_func.kakunin(userid, userpass):
        pass
    else:
        sentence = '接続できません。最初の画面からやり直してください。'
        return make_response(render_template('error.html',
                                             sentence = sentence))
    
    ## 不正入力処理
    if len(request.form['text']) == 0:
        sentence = 'ERROR： 情報を送信できませんでした。すべての情報を正しく入力しましたか？'\
           +'(detail: トレーニングメニューが入力されていません。)'
           
        return make_response(render_template('error.html',
                                             sentence = sentence))
    
    if float(request.form['wb']) <= 0 or float(request.form['wb']) <= 0:
        sentence = '''ERROR： 情報を送信できませんでした。
         (detail: あなたの体重が{}kgと{}kgになっています。
         そんなわけありません!!!。)'''.format(request.form['wb'],request.form['wa'])
        return make_response(render_template('error.html',sentence=sentence))
    
    if request.form['time'] == '' \
        or request.form['temp'] == '' \
            or request.form['sitsu'] == ''\
                or request.form['moi'] == '':
        sentence = 'ERROR： 情報を送信できませんでした。すべての情報を正しく入力しましたか？'\
                +'(detail: トレーニング時間、飲水量、気温、湿度のいずれかが未入力です。)'
        return make_response(render_template('error.html',sentence=sentence))
    if float(request.form['time']) < 0 or float(request.form['moi']) < 0:
        sentence = 'ERROR： 情報を送信できませんでした。'\
                + '(detail: 運動時間または飲水量を正の値にしてください。)'
        return make_response(render_template('error.html',sentence=sentence))
    ##
    try:
        weight_after  = float(request.form['wa'])
        weight_before = float(request.form['wb'])
        time          = float(request.form['time'])
        moisture      = float(request.form['moi'])
        shitsudo      = float(request.form['sitsu'])
        temp          = float(request.form['temp'])
        contents      = str(request.form['text'])
        tenki         = int(request.form['tenki'])
        
        my_func.sql_data_send(userid,#ログインするユーザ
                              userpass,#ログインするユーザのパス
                              weight_before,
                              weight_after,
                              contents,time,
                              moisture,tenki,
                              shitsudo,
                              temp)
        
        data = my_func.sql_data_get(userid)
        
        posts = []
        for d in reversed(data):
            neccessary1_tmp = round(float(d['wb'] * 0.99) \
                                    - float(d['wa']) + float(d['moi']), 1)
            if neccessary1_tmp <= 0:
                neccessary1_tmp = 0
                
            posts.append({
                  'date'         :d['day'],#日
                  'bweight'      :d['wb'],#運動前体重
                  'aweight'      :d['wa'],#運動後体重
                  'training'     :d['contents'][0:10],#トレーニング内容
                  'period'       :d['time'],#運動時間
                  'intake'       :d['moi'],#飲水量
                  'dehydraterate':my_func.dassui_ritu(d['wb'], d['wa']),#脱水率
                  'tenki'        :str(tenki_dic[str(d['tenki'])]),#天気
                  'shitsudo'     :d['shitsudo'],#湿度
                  'temp'         :d['temp'],
                  'dassui1'      :round(my_func.hakkann_ritu_ex1(d['wb'], d['wa'], d['time']), 1),
                  'necessary'    :round(my_func.hakkann_ryo(d['wb'], d['wa'], d['moi']), 1),
                  'necessary1'   :neccessary1_tmp,
                  'w1'           :round(d['wb'] * 0.99, 1)})
                
        redirect_to_index = redirect('/show',code=307)
        resp = make_response(redirect_to_index)
        resp.set_cookie('user', userid)
        resp.set_cookie('pass', userpass)
        # showへリダイレクト
        return resp
    
    except Exception as error:
        sentence = 'ERROR： 情報を送信できませんでした。すべての情報を正しく入力しましたか？' \
                    +'(detail: '+error.__str__()+')'
        
        index = render_template('error.html',
                                sentence = sentence)
        
        return make_response(index)












# for administration
# 全てのユーザのプロフィールを取得：本名，組織，年度
# user_prof = {}

# 管理者mainページ
@app.route("/admin/show", methods = ["POST"])
def admin_show():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    
    try:
        if my_func.admin_coach_kakunin(admin, adminpass):
            index = render_template('admin_main.html',
                                    title = 'taberube.jp for admin',
                                    user = admin,
                                    posts = [],
                                    serverhost = server_address)
            
            resp = make_response(index)
            resp.set_cookie('user', admin)
            resp.set_cookie('pass', adminpass)
        else:
            sentence = '管理者または監督・コーチのみログインできます。'
            index = render_template('error.html',
                                    sentence = sentence)
            resp = make_response(index)
        
    except Exception as error:
        sentence = 'do not connect sql server by your username \
                \n or making html error:\n{}'.format(error.__str__())
        index = render_template('error.html',
                                sentence = sentence)
        resp = make_response(index)
    
    return resp

    
# 管理者用アプリWatch
@app.route("/admin/watch", methods = ["POST"])
def admin_watch():# ユーザリスト　ユーザを選び -> admin_watch_show()
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    
    try:
        if not(my_func.admin_coach_kakunin(admin, adminpass)):
            sentence = '初めからやり直してください。'
            index = render_template('error.html',
                                    sentence = sentence)
            return make_response(index)
        user_prof = my_func.sql_ALLuser_profile()
        org_dic = my_func.get_org()
        
    except Exception as error:
        sentence = 'do not connect sql server by your username \
                \n or occur making html error:\n{}'.format(error.__str__())
        index = render_template('error.html',
                                sentence = sentence)
        resp = make_response(index)
    
    posts = []; posts_admin = [] 
    posts_coach = []; posts_unusable = []
    
    for name in user_prof.keys():
        dic = {'name'     :user_prof[name]['rname'],
                'org'     :org_dic[user_prof[name]['org']]['org_name'],
                'year'    :user_prof[name]['year'],
                'id'      :name,
                'keyword' :str(user_prof[name]['year']) \
                     + user_prof[name]['org'] + name,
               }
        if user_prof[admin]['type'] == 2 \
            and dic['org'] == org_dic[user_prof[admin]['org']]['org_name']:
            
            if user_prof[name]['type'] == 1:
                posts.append(dic)
            elif user_prof[name]['type'] == 2:
                posts_coach.append(dic)
            
        if user_prof[admin]['type'] == 0:
            
            if user_prof[name]['type'] == 0:
                posts_admin.append(dic)
            elif user_prof[name]['type'] == 1:
                posts.append(dic)
            elif user_prof[name]['type'] == 2:
                posts_coach.append(dic)
            elif user_prof[name]['type'] == -1:
                posts_unusable.append(dic)
    
    if user_prof[admin]['type'] == 2:
        posts_admin =[{'name':'非表示',
                       'org' :'XXXX',
                       'year':'XXXX',
                       'id'  :'XXXX'}]; 
    
    posts = reversed(sorted(posts, 
                            key = lambda x : x['keyword'])
            )
    resp = make_response(render_template(
            'admin_watch.html',
            serverhost = server_address,
            posts = posts,
            posts_admin = posts_admin,
            posts_coach = posts_coach,
            posts_unusable = posts_unusable))
    
    return resp

# 管理者用アプリwatchの内部機能 各ユーザの結果を見る
@app.route("/admin/watch/show", methods = ["GET", "POST"])
def admin_watch_show():
    admin = request.cookies.get('user')# クッキーを保存
    adminpass = request.cookies.get('pass')# クッキーを保存
    
    if not(my_func.admin_coach_kakunin(admin, adminpass)):
        sentence = '初めからやり直してください。'
        index = render_template('error.html',
                                sentence = sentence)
        return make_response(index)
    
    try:
        user_prof = my_func.sql_ALLuser_profile()
        uid_get = request.args.get('name')#　見たいユーザ名
        real_name = user_prof[uid_get]['rname']# ユーザの本名
        
        if user_prof[admin]['type'] == 2 and user_prof[admin]['org'] != user_prof[uid_get]['org']:
            sentence = '機能制限： このユーザーのデータは閲覧できません。'
            index = render_template('error.html',
                                    sentence = sentence)
            return make_response(index)
        
        data = my_func.sql_data_get(uid_get)
        posts = []
        for d in reversed(data):# dataは辞書形式
            neccessary1_tmp \
                = round(float(d['wb']*0.01) + float(d['moi']), 1)
            
            if neccessary1_tmp <= 0:
                neccessary1_tmp = 0
            shitsudo = d['shitsudo']
            temp = d['temp']
            if int(shitsudo) == 1111:
                shitsudo = ' '
            if int(temp) == 1111:
                temp = ' '
            
            posts.append({
              'date'          :d['day'],#日
              'bweight'       :d['wb'],#運動前体重
              'aweight'       :d['wa'],#運動後体重
              'training'      :d['contents'][0:10],#トレーニング内容
              'period'        :d['time'],#運動時間
              'intake'        :d['moi'],#飲水量
              'dehydraterate' :my_func.dassui_ritu(d['wb'],d['wa']),#脱水率
              'necessary'    :round(my_func.hakkann_ryo(d['wb'], d['wa'], d['moi']), 1),
              'tenki'         :tenki_dic[str(d['tenki'])],#天気
              'shitsudo'      :shitsudo,#湿度
              'temp'          :temp,
              'w1'            :round(d['wb']*0.99,1),
              'necessary1'    :neccessary1_tmp
            })
        
        index = render_template('admin_show.html',
                                title = 'taberube.jp',
                                user = real_name,
                                posts = posts,
                                userid = uid_get,
                                serverhost = server_address)
        
        resp = make_response(index)
        
        resp.set_cookie('user', admin)# クッキーの再設定
        resp.set_cookie('pass', adminpass)# クッキーの再設定
        
        return resp
    except Exception as error:# SQLなどのエラー
        sentence = error.__str__()
        index = render_template('error.html',
                                sentence = sentence)
        return make_response(index)


# 管理者用アプリNew!(過去2日の投稿を表示)
@app.route("/admin/latest", methods = ["POST"])
def admin_latest():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    
    if admin == '' or adminpass == '':
        sentence = 'ログアウトしています。'
        index = render_template('error.html',
                                sentence = sentence)
        return make_response(index)
    
    if not (my_func.admin_coach_kakunin(admin, adminpass)):
        sentence = '初めからやり直してください。'
        index = render_template('error.html',
                                sentence = sentence)
        return make_response(index)
    
    try:
        user_prof = my_func.sql_ALLuser_profile()
        try:
            data = my_func.sql_data_get_latest_all(user_prof[admin]['type'],
                                                   user_prof[admin]['org'])
            posts = []
            for d in reversed(data):
                neccessary1_tmp \
                    = round(float(d['wb']*0.01) + float(d['moi']),1)
                if neccessary1_tmp <= 0:
                    neccessary1_tmp = 0
                shitsudo = d['shitsudo']
                temp = d['temp']
                if int(shitsudo) == 1111:
                    shitsudo = ' '
                if int(temp) == 1111:
                    temp = ' '
                posts.append({
                  'date'         :d['day'],#日
                  'bweight'      :d['wb'],#運動前体重
                  'aweight'      :d['wa'],#運動後体重
                  'training'     :d['contents'][0:10],#トレーニング内容
                  'period'       :d['time'],#運動時間
                  'intake'       :d['moi'],#飲水量
                  'dehydraterate':my_func.dassui_ritu(d['wb'],d['wa']),#脱水率
                  'necessary'    :round(my_func.hakkann_ryo(d['wb'], d['wa'], d['moi']), 1),
                  'tenki'        :tenki_dic[str(d['tenki'])],#天気
                  'shitsudo'     :shitsudo,#湿度
                  'temp'         :temp,
                  'username'     :user_prof[d['username']]['rname'],
                  'w1'           :round(d['wb']*0.99,1),
                  'necessary1'   :neccessary1_tmp}# ユーザの本名
                )
            
            posts = reversed(sorted(posts, key=lambda x:x['date']))
            index = render_template('admin_latest.html', 
                                    title = 'taberube.jp', 
                                    posts = posts,
                                    serverhost = server_address)
            return make_response(index)
            
        except Exception as error:
            sentence = 'ERROR1: ' + error.__str__()
            index = render_template('error.html',
                                    sentence = sentence)
            return make_response(index)
        
    except Exception as error:
            sentence = 'ERROR2: '+error.__str__()
            index = render_template('error.html',
                                    sentence = sentence)
            return make_response(index)

# 管理者用アプリRegister，新規ユーザー追加
@app.route("/admin/register",
           methods = ["GET", "POST"])
def admin_register():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    text = ''
    
    if not (my_func.admin_kakunin(admin, adminpass)):
        sentence = '機能制限： ユーザー管理機能は管理者のみ利用可能です。'
        index = render_template('error.html',
                                sentence = sentence)
        return make_response(index)
    
    if len(admin) == 0 or len(adminpass) == 0:
        return 'NG1: cannot access'
    
    if request.args.get('resgs') == 'org':
        if len(request.form['org_id']) == 0 \
            or len(request.form['org_name']) == 0:
            sentence = 'ERROR : Fill in the blank!: すべての空欄を埋めてください。'
            index = render_template('error.html',
                                    sentence = sentence)
            return make_response(index)
        
        if request.form['org_id'] in my_func.get_org().keys():
            sentence = '''
                        NG: 新しい組織を登録できません。
                        組織ID[{}]は使われています。違う組織名を指定してください。
                        '''.format(request.form['org_id'])
            index = render_template('error.html',
                                    sentence = sentence)
            return make_response(index)
        
        try:
            info = {'org_id':request.form['org_id'],
                    'org_name':request.form['org_name']}
            my_func.addorg(admin, adminpass, info)
            
        except Exception as error:
            sentence = 'ERROR: ' + error.__str__()
            index = render_template('error.html',
                                    sentence = sentence)
            return make_response(index)
    
    if request.args.get('resgs') == 'user':
        # ユーザーの登録
        info = {'newuser':request.form['newuser'],
                'newpass':request.form['newpass'],
                'rname'  :request.form['rname'],
                'type'   :request.form['type'],
                'org'    :request.form['org'],
                'year'   :request.form['year']
                }
        
        if len(request.form['newuser']) == 0 or len(request.form['newpass']) == 0 or \
            len(request.form['rname']) == 0 or len(request.form['org']) == 0:
            
            sentence = 'ERROR : Fill in the blank!: すべての空欄を埋めてください。'
            index = render_template('error.html',
                                    sentence = sentence)
            return make_response(index)
        
        if request.form['newuser'] in my_func.sql_ALLuser_profile().keys():
            sentence = '''
                        NG: 新しいユーザーを登録できません。
                        ユーザー名[{}]は使われています。違うユーザー名を指定してください。
                        '''.format(request.form['newuser'])
            index = render_template('error.html',
                                    sentence = sentence)
            return make_response(index)
        
        try:
            if my_func.adduser(admin, adminpass, info):
                text = request.form['rname'] + 'さんを登録しました．',

            else:
                return 'NG'
        except Exception as error:
            return 'Fail: SQL Server Error' + error.__str__()
    
    user_prof = my_func.sql_ALLuser_profile()
    org_dic = my_func.get_org()
    
    posts = []; posts_admin = [] 
    posts_coach = []; posts_unusable = []
    posts_org = []
    
    for name in user_prof.keys():
        dic = {'name':user_prof[name]['rname'],
                'org':org_dic[user_prof[name]['org']]['org_name'],
                'year':user_prof[name]['year'],
                'id':name,
                'keyword':str(user_prof[name]['year']) \
                     + user_prof[name]['org'] + name,
               }
        
        if user_prof[name]['type'] == 0:
            posts_admin.append(dic)
        elif user_prof[name]['type'] == 1:
            posts.append(dic)
        elif user_prof[name]['type'] == 2:
            posts_coach.append(dic)
        elif user_prof[name]['type'] == -1:
            posts_unusable.append(dic)
    
    
    for p in org_dic.keys():
        dic = {'org_id'  :p,
               'org_name':org_dic[p]['org_name']}
        
        posts_org.append(dic)
        
    posts = reversed(sorted(posts, key = lambda x:x['keyword']))
    
    index = render_template('admin_register.html',
                            text = text,
                            serverhost = server_address,
                            posts = posts,
                            posts_admin = posts_admin,
                            posts_coach = posts_coach,
                            posts_unusable = posts_unusable,
                            posts_org = posts_org,
                            year = datetime.datetime.now().year)
    
    resp = make_response(index)
    
    return resp

@app.route("/admin/account", methods = ["GET","POST"])
def admin_account_change():
    userid = request.cookies.get('user')
    userpass = request.cookies.get('pass')
    
    u_id = request.args.get('name')
    if request.args.get('op') == 'stop':
        my_func.update_user(userid, userpass, u_id, 'stop')
    elif request.args.get('op') == 'user':
        my_func.update_user(userid, userpass, u_id, 'user')
    elif request.args.get('op') == 'coach':
        my_func.update_user(userid, userpass, u_id, 'coach')
    elif request.args.get('op') == 'admin':
        my_func.update_user(userid, userpass, u_id, 'admin')
    
    redirect_to_index = redirect('/admin/register?status=first', code=307)
    
    resp = make_response(redirect_to_index)
    resp.set_cookie('user', userid)
    resp.set_cookie('pass', userpass)
    return resp


# 管理者用アプリ Message, 管理者から全体への連絡事項を追加
@app.route("/admin/message", methods = ["GET", "POST"])
def admin_message():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    user_prof = my_func.sql_ALLuser_profile()
    
    #if my_func.admin_coach_kakunin(admin, adminpass):
    if my_func.admin_kakunin(admin, adminpass):
        pass
    else:
        sentence = '改修中です。監督・コーチの掲示板の機能のご利用はもうしばらくお待ちください。'
        index = render_template('error.html',
                                sentence = sentence)
        return make_response(index)
    
    messages = my_func.sql_message_get(
        admin,
        adminpass,
        max_messages = 10
    )
    
    posts = []
    for d in messages:
        posts.append({
            'day'     :d['day'],
            'rname'   :user_prof[d['userid']]['rname'],
            'group'   :d['group'],
            'title'   :d['title'],
            'contents':d['contents']}
        )
    
    if request.args.get('status') == 'first':
        try:
            my_func.kakunin(admin, adminpass)
        except Exception as error:
            return 'NG: '+error.__str__()
        index = render_template('admin_message.html',
                                serverhost = server_address,
                                posts = posts)
        resp = make_response(index)
        
        return resp
    
    try:
        if len(admin) == 0 or len(adminpass) == 0:
            return 'Cannot access message'
        
        # you have to add form of group below
        group = 'ALL'
        title = str(request.form['title'])
        contents = str(request.form['contents'])
        
        my_func.sql_message_send(
            admin, 
            adminpass, 
            group,
            title, 
            contents,
        )
        
        messages = my_func.sql_message_get(
                admin,
                adminpass,
                max_messages = 10
                )
        
        posts = []
        for d in messages:
            posts.append({
                'day'     :d['day'],
                'rname'   :user_prof[d['userid']]['rname'],
                'group'   :d['group'],
                'title'   :d['title'],
                'contents':d['contents']}
            )
        
        return render_template(
                'admin_message.html', 
                 title = 'Message',
                 user = admin,
                 posts = posts,
                 serverhost = server_address
                 )
    except Exception as error:
        return error.__str__()

# 管理者用アプリAnalysis，簡単な統計，解析
@app.route("/admin/analysis", methods = ["GET","POST"])
def admin_analysis():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    
    if my_func.admin_coach_kakunin(admin, adminpass) \
        and not(len(admin) == 0 or len(adminpass) == 0):
        pass
    else:
        sentence = '初めからやり直してください。'
        index = render_template('error.html',
                                sentence = sentence)
        return make_response(index)
    
    day_list = []
    data_list = []
    for i in range(31):
        day = datetime.date.today() - datetime.timedelta(days=i)
        strday = day.strftime("%Y-%m-%d")
        data = my_func.sql_data_per_day(strday)
        dassui_data = [100*float((d['wa']-d['wb'])/d['wb']) for d in data]
        day_list.append(day.strftime("%m/%d"))
        if i == 0:
            today_list = dassui_data
        if len(dassui_data) > 0:
            data_list.append(float(sum(dassui_data) / len(dassui_data)))
        else:
            data_list.append(float(-100))
    # 脱水率平均の図を出力
    data_list.reverse()
    day_list.reverse()
    
    plt.figure()
    plt.plot(data_list,'o')
    plt.xticks(range(0,31)[::3], day_list[::3])
    plt.grid(color = 'gray')
    plt.ylim(-2.5,1.5)
    plt.ylabel('Dehydration rate')
    plt.xlabel('Date')
    plt.title('Daily average')
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S")\
                + 'ave.png'
    path_list = glob.glob('./static/img/analysis/*.png')
    for file in path_list:
        os.remove(file)
    plt.savefig('./static/img/analysis/'+filename)
    # 散布図
    plt.figure()
    plt.hist(today_list,bins=10,range=(-2,2))
    plt.ylabel('Frequency')
    plt.xlabel('Dehydration rate')
    plt.ylim(0,)
    plt.xlim(-2,2)
    plt.title('Today\'s Scatter plot')
    filename2 = datetime.datetime.now().strftime("%Y%m%d%H%M%S")\
                +'scatter.png'
    plt.savefig('./static/img/analysis/'+filename2)
    
    return make_response(render_template('admin_analysis.html',
                                         fname=filename,
                                         fname2=filename2))
# データのダウンロード
@app.route("/admin/download", methods=["GET","POST"])
def admin_download():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    
    if my_func.admin_kakunin(admin, adminpass) \
        and not(len(admin) == 0 or len(adminpass) == 0):
        pass
    else:
        sentence = '機能制限： この機能は管理者のみが利用可能です。'
        index = render_template('error.html',
                                sentence = sentence)
        return make_response(index)
    resp = make_response()
    
    file = request.args.get('file')
    name = request.args.get('name')
    ## SQL####
    try:
        my_func.sql_makecsv(file, name)
    except Exception as error:
        sentence = 'ERROR: CSVファイルを作成できません。' \
                        + error.__str__()
        index = render_template('error.html', 
                                sentence = sentence)
        return make_response(index)
    ######
    
    if file == 'data':
        if name == None:
            downloadFileName = "data_ALL.csv"
        else:
            downloadFileName = "data_{}.csv".format(name)
            
        resp.data = open(downloadFileName, "rb").read()
    
    elif file == 'user':
        resp.data = open("./user_list.csv", "rb").read()
        downloadFileName = 'user.csv'
    resp.headers['Content-Disposition'] = 'attachment; filename=' + downloadFileName
    resp.mimetype = 'text/csv'
    return resp

if __name__ == "__main__":
    app.run(debug = False,
            host = server_host,
            port = server_port,
            threaded = True)
