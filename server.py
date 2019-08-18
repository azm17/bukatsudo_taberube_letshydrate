# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 17:56:33 2019

@author: Azumi Mamiya 
         Daiki Miyagawa
         Kenshin Iwakura

pip3 install flask
pip3 install mysql-connector-python
pip3 import datetime
"""

from flask import Flask,request,render_template,make_response,redirect
import my_function2_sql as my_func
import datetime
import matplotlib.pyplot as plt
import os
import glob


app = Flask(__name__)
#server host
#server_host='192.168.0.15'
server_host='192.168.2.102'
#server_host='192.168.56.1'
#server_host='192.168.0.6'
#server_host='test-server0701.herokuapp.com'


# serverport
server_port=50000
server_address=server_host+':'+str(server_port)
#server_address=server_host

#SQL server
SQLserver_host='192.168.0.32'
SQLserver_port=3306
database_name='hydration_db'
sql_userid='sql_azumi'
sql_userpass='sql_mamiya'

tenki_dic={'1':'🌞️','2':'☁️','3':'🌧️','4':'❄️'}
# 一般ユーザーログイン画面送信
@app.route("/")
def entry():
    resp = make_response(render_template('index.html',
                                         serverhost=server_address))
    resp.set_cookie('user', '')
    resp.set_cookie('pass', '')
    return resp

# 
@app.route("/hello", methods=["GET","POST"])
def hello():
    userid = request.cookies.get('user')
    userpass = request.cookies.get('pass')
    hantei=my_func.kakunin(userid,userpass)
    user_prof=my_func.sql_ALLuser_profile(id, userpass)
    
    print("ID:{} TRY LOGIN ".format(userid)+str(hantei))
    if hantei:# lonin success
       #templist=[round(i/5-10,1) for i in range(276)]
        #11~3月のみ雪マークを追加
        weather=[{'num':'{}'.format(i),'moji':tenki_dic[i]}
                    for i in tenki_dic.keys()
                        if not(4<=datetime.datetime.today().month<=10) and i=='4' 
                            or i=='1' or i=='2' or i=='3']
        water=['{:.2f}'.format(round(i*0.05,2)) for i in range(201)]
        return render_template('hello.html', 
                               title='flask test', 
                               name=user_prof[userid]['rname'],
                               weather=weather,
                               water=water,
                               serverhost=server_address)
    else:# login fail
        sentence='接続できません。最初からやり直してください。'
        return make_response(render_template('error.html',sentence=sentence))

# 一般ユーザーの結果（表）画面
@app.route("/show", methods=["POST"])
def show():
    try:
        userid = request.form['user']
        userpass = request.form['pass']
    except:
        userid = request.cookies.get('user')
        userpass = request.cookies.get('pass')
        
    user_prof=my_func.sql_ALLuser_profile(userid, userpass)
    
    if my_func.kakunin(userid,userpass):
        pass
    else:
        sentence='IDまたはPASSが違います。正しいパスワードを入力してください。'
        resp = make_response(render_template('error.html',
                                         sentence=sentence))
        return resp  
    print("ID:{} GET ".format(userid),end='')
    try:
        data=my_func.sql_data_get(userid)
        posts=[]
        for d in reversed(data):
            neccessary1_tmp=round(float(d['wb']*0.99)-float(d['wa'])+float(d['moi']),1)
            if neccessary1_tmp<=0:
                neccessary1_tmp=0
            posts.append({
                  'date' : d['day'],#日
                  'bweight' : d['wb'],#運動前体重
                  'aweight' : d['wa'],#運動後体重
                  'training' : d['contents'][0:10],#トレーニング内容
                  'period' : d['time'],#運動時間
                  'intake' : d['moi'],#飲水量
                  'dehydraterate' : my_func.dassui_ritu(d['wb'],d['wa']),#脱水率
                  'dehydrateval' : str(round(float(d['wb'])-float(d['wa']),1)),#脱水量
                  'tenki':str(tenki_dic[str(d['tenki'])]),#天気
                  'shitsudo':d['shitsudo'],#湿度
                  'temp':d['temp'],
                  'dassui1':round(my_func.hakkann_ritu_ex1(d['wb'],d['wa'],d['time']),1),
                  'necessary':round(my_func.hakkann_ryo(d['wb'],d['wa'],d['moi']),1),
                  'necessary1':neccessary1_tmp,
                  'w1':round(d['wb']*0.99,1)
                })
        if len(posts)>0:
            latest=posts.pop(0)
            data=my_func.generateComment(latest)
            comment=data['sentence']
            img=data['img']
            
        else:
            latest={
                  'date' : '今回',#日
                  'bweight' : 'No data',#運動前体重
                  'aweight' : 'No data',#運動後体重
                  'training' : 'No data',#トレーニング内容
                  'period' : 'No data',#運動時間
                  'intake' : 'No data',#飲水量
                  'dehydraterate' : 'No data',#脱水率
                  'dehydrateval' : 'No data',#脱水量
                  'tenki':'No data',#天気
                  'shitsudo':'No data',#湿度
                  'temp':'No data',
                  'dassui1':'No data',
                  'necessary':'No data',
                  'necessary1':'No data',
                  'w1':'No data'}
            comment='''初めまして。このアプリでは、
                日々のトレーニング後の脱水量を記録していきます。
                最初のデータを入力しましょう。
                下の「データ入力」ボタンから結果を登録できます。
                また、「皆さんへの連絡」は、このアプリを利用している全員向けのコメントです。'''
            
            img='suzuki1.png'
        messages=my_func.sql_message_get(
                userid,
                userpass,
                max_messages = 3)
        
        texts=[]
        for d in messages:
            texts.append({
                'day': d['day'],
                'rname': user_prof[d['userid']]['rname'],
                'group': d['group'],
                'title': d['title'],
                'contents': d['contents']}
            )
        print('Success')
        
        resp = make_response(render_template('main.html',
                                             title='My Title',
                                             user=userid,
                                             posts=posts,
                                             latest=latest,
                                             comment=comment,
                                             texts=texts,
                                             img=img,
                                             rname=user_prof[userid]['rname'],
                                             serverhost=server_address))
        resp.set_cookie('user', userid)
        resp.set_cookie('pass', userpass)
        
        return resp
    except Exception as error:
        sentence='''エラー: 結果の画面が取得できません。
        SQLサーバーが停止している、または、
        表データに不正な文字が含まれているため表示できません。 
        サーバー側に問題があるので、管理者にお問い合わせください。(detail:'''+error.__str__()+')'
        return make_response(render_template('error.html',sentence=sentence))

# 情報入力
@app.route("/enter", methods=["GET","POST"])
def enter():
    userid = request.cookies.get('user')
    userpass = request.cookies.get('pass')
    
    if my_func.kakunin(userid,userpass):
        pass
    else:
        sentence='接続できません。最初の画面からやり直してください。'
        return make_response(render_template('error.html',sentence=sentence))
    
    ## 不正入力処理
    if len(request.form['text'])==0:
        sentence='ERROR： 情報を送信できませんでした。すべての情報を正しく入力しましたか？'+'(detail: トレーニングメニューが入力されていません。)'
        return make_response(render_template('error.html',sentence=sentence))
    if float(request.form['wb'])<=0 or float(request.form['wb'])<=0:
        sentence='''ERROR： 情報を送信できませんでした。
        (detail: あなたの体重が{}kgと{}kgになっています。
        そんなわけありません。)'''.format(request.form['wb'],request.form['wa'])
        return make_response(render_template('error.html',sentence=sentence))
    print(request.form['time'])
    if request.form['time']=='' \
        or request.form['temp']=='' \
            or request.form['sitsu']==''\
                or request.form['moi']=='':
        sentence='ERROR： 情報を送信できませんでした。すべての情報を正しく入力しましたか？'\
                +'(detail: トレーニング時間、飲水量、気温、湿度のいずれかが未入力です。)'
        return make_response(render_template('error.html',sentence=sentence))
    if float(request.form['time'])<0 or float(request.form['moi'])<0:
        sentence='ERROR： 情報を送信できませんでした。'+'(detail: 運動時間または飲水量を正の値にしてください。)'
        return make_response(render_template('error.html',sentence=sentence))
    ##
    print("ID:{} GET ".format(userid))
    try:
        weight_after= float(request.form['wa'])
        weight_before= float(request.form['wb'])
        contents= str(request.form['text'])
        time= float(request.form['time'])
        moisture= float(request.form['moi'])
        tenki= int(request.form['tenki'])
        shitsudo= float(request.form['sitsu'])
        temp=float(request.form['temp'])
        my_func.sql_data_send(userid,#ログインするユーザ
                              userpass,#ログインするユーザのパス
                              weight_before,
                              weight_after,
                              contents,time,
                              moisture,tenki,
                              shitsudo,
                              temp)
        
        
        data=my_func.sql_data_get(userid)
        
        posts=[]
        for d in reversed(data):
            neccessary1_tmp=round(float(d['wb']*0.99)-float(d['wa'])+float(d['moi']),1)
            if neccessary1_tmp<=0:
                neccessary1_tmp=0
            posts.append({
                  'date' : d['day'],#日
                  'bweight' : d['wb'],#運動前体重
                  'aweight' : d['wa'],#運動後体重
                  'training' : d['contents'][0:10],#トレーニング内容
                  'period' : d['time'],#運動時間
                  'intake' : d['moi'],#飲水量
                  'dehydraterate' : my_func.dassui_ritu(d['wb'],d['wa']),#脱水率
                  'dehydrateval' : str(round(float(d['wb'])-float(d['wa']),1)),#脱水量
                  'tenki':str(tenki_dic[str(d['tenki'])]),#天気
                  'shitsudo':d['shitsudo'],#湿度
                  'temp':d['temp'],
                  'dassui1':round(my_func.hakkann_ritu_ex1(d['wb'],d['wa'],d['time']),1),
                  'necessary':round(my_func.hakkann_ryo(d['wb'],d['wa'],d['moi']),1),
                  'necessary1':neccessary1_tmp,
                  'w1':round(d['wb']*0.99,1)})
                
        redirect_to_index = redirect('/show',code=307)
        resp=make_response(redirect_to_index)
        resp.set_cookie('user', userid)
        resp.set_cookie('pass', userpass)
        #showへリダイレクト
        return resp
    
    except Exception as error:
        sentence='ERROR： 情報を送信できませんでした。すべての情報を正しく入力しましたか？'+'(detail: '+error.__str__()+')'
        return make_response(render_template('error.html',sentence=sentence))

# for administration
#全てのユーザのプロフィールを取得：本名，組織，年度
#user_prof={}
# 管理者ログインページ
@app.route("/admin")
@app.route("/admin/")
def admin_entry():
    resp = make_response(render_template('admin_index.html',
                                         serverhost=server_address))
    resp.set_cookie('user', '')
    resp.set_cookie('pass', '')
    return resp

# 管理者ホームページ
@app.route("/admin/show",methods=["POST"])
def admin_show():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
        
    if admin == '' or adminpass == '':
        admin = request.form['user']
        adminpass = request.form['pass']
    
    if my_func.admin_kakunin(admin, adminpass):
        pass
    else:
        sentence='管理者用のログイン画面です。正しいIDとPASSを入力してください。'
        return make_response(render_template('error.html',sentence=sentence))
        
    posts=[]
    print("ID:{} GET ".format(admin),end='')
    if admin == '' or adminpass == '':
        sentence='正しいIDとPASSを入力してください。'
        return make_response(render_template('error.html',sentence=sentence))
    administrators=my_func.get_admin()
    if admin in administrators: 
        try:
            hantei=my_func.kakunin(admin,adminpass)
            
            resp = make_response(render_template('admin_main.html',
                                                 title='Admin',
                                                 user=admin,
                                                 posts=posts,
                                                 serverhost=server_address))
            resp.set_cookie('user', admin)
            resp.set_cookie('pass', adminpass)
            
            if hantei:
                return resp
            sentence='正しいIDとPASSを入力してください。'
            return make_response(render_template('error.html',sentence=sentence))
        except Exception as error:
            print('Fail')
            sentence='do not connect sql server by your username \
                    \n or making html error:\n{}'.format(error.__str__())
            return make_response(render_template('error.html',sentence=sentence))
    else:
        sentence='you are not an administrator'
        return make_response(render_template('error.html',sentence=sentence))
    
# 管理者用アプリWatch
@app.route("/admin/watch", methods=["POST"])
def admin_watch():# ユーザリスト　ユーザを選び->admin_watch_show()
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    user_prof=my_func.sql_ALLuser_profile(admin,adminpass)
    
    if my_func.admin_kakunin(admin, adminpass):
        pass
    else:
        sentence='初めからやり直してください。'
        return make_response(render_template('error.html',sentence=sentence))
    
    if admin == '' or adminpass == '':
        # 不正アクセス（クッキーが空など，ユーザ名，パスワード未設定）
        sentence='NG: cannot access /watch'
        return make_response(render_template('error.html',sentence=sentence))
    
    try:
        my_func.kakunin(admin,adminpass)
    except Exception as error:
        #接続失敗，SQLに接続できないなど
        sentence='ERORR: '+error.__str__()
        return make_response(render_template('error.html',sentence=sentence))
    
    
    posts= [{'name':user_prof[name]['rname'],
             'org':user_prof[name]['org'],
             'year':user_prof[name]['year'],
             'id':name,
             'keyword':str(user_prof[name]['year'])+user_prof[name]['org']+name,
             } for name in user_prof.keys()
    ]
    posts = reversed(sorted(posts, key=lambda x:x['keyword']))
    resp = make_response(render_template(
            'admin_watch.html',
            serverhost=server_address,
            posts=posts))
    
    return resp

# 管理者用アプリwatchの内部機能 各ユーザの結果を見る
@app.route("/admin/watch/show", methods=["GET","POST"])
def admin_watch_show():
    admin = request.cookies.get('user')# クッキーを保存
    adminpass = request.cookies.get('pass')# クッキーを保存
    user_prof = my_func.sql_ALLuser_profile(admin, adminpass)
    
    if my_func.admin_kakunin(admin, adminpass):
        pass
    else:
        sentence='初めからやり直してください。'
        return make_response(render_template('error.html',sentence=sentence))
    
    if admin != '' and adminpass != '':
        #SQLサーバ接続テスト：ユーザ名，パスワードの整合性の確認
        my_func.kakunin(admin,adminpass)
        uid_get=request.args.get('name')#　見たいユーザ名
        real_name=user_prof[uid_get]['rname']# 見たいユーザの本名
        
        try:
            data=my_func.sql_data_get(uid_get)
            posts=[]
            for d in reversed(data):#dataは辞書形式
                posts.append({
                  'date' : d['day'],#日
                  'bweight' : d['wb'],#運動前体重
                  'aweight' : d['wa'],#運動後体重
                  'training' : d['contents'][0:10],#トレーニング内容
                  'period' : d['time'],#運動時間
                  'intake' : d['moi'],#飲水量
                  'dehydraterate' : my_func.dassui_ritu(d['wb'],d['wa']),#脱水率
                  'dehydrateval' : str(round(float(d['wb'])-float(d['wa']),1)),#脱水量
                  'tenki':d['tenki'],#天気
                  'shitsudo':d['shitsudo'],#湿度
                  'temp':d['temp']
                })
            print('Success')
            
            resp = make_response(
                    render_template(
                            'admin_show.html',
                            title='My Title', 
                            user=real_name,
                            posts=posts,
                            serverhost=server_address
                            )
                    )
            
            resp.set_cookie('user', admin)# クッキーの再設定
            resp.set_cookie('pass', adminpass)# クッキーの再設定
            
            return resp
        except Exception as error:# SQLなどのエラー
            return error.__str__()
    else:
        # 不正アクセス（クッキーが空など，ユーザ名，パスワード未設定）
        sentence='NG: cannot access watch/show'
        return make_response(render_template('error.html',sentence=sentence))

# 管理者用アプリNew!(過去2日の投稿を表示)
@app.route("/admin/latest", methods=["POST"])
def admin_latest():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    user_prof=my_func.sql_ALLuser_profile(admin, adminpass)
    
    if admin=='' or adminpass=='':
        sentence='cannot access!'
        return make_response(render_template('error.html',sentence=sentence))
    
    if my_func.admin_kakunin(admin, adminpass):
        pass
    else:
        sentence='初めからやり直してください。'
        return make_response(render_template('error.html',sentence=sentence))
    
    try:
        print('Success')
        try:
            data=my_func.sql_data_get_latest_all()
            posts=[]
            for d in reversed(data):
                posts.append({
                  'date':d['day'],#日
                  'bweight':d['wb'],#運動前体重
                  'aweight':d['wa'],#運動後体重
                  'training':d['contents'][0:10],#トレーニング内容
                  'period':d['time'],#運動時間
                  'intake':d['moi'],#飲水量
                  'dehydraterate':my_func.dassui_ritu(d['wb'],d['wa']),#脱水率
                  'dehydrateval':str(round(float(d['wb'])-float(d['wa']),1)),#脱水量
                  'tenki':tenki_dic[str(d['tenki'])],#天気
                  'shitsudo':d['shitsudo'],#湿度
                  'temp':d['temp'],
                  'username':user_prof[d['username']]['rname']}# ユーザの本名
                )
            print('Success')
            posts = reversed(sorted(posts, key=lambda x:x['date']))
            return render_template(
                    'admin_latest.html', 
                    title='Latest posts', 
                    posts=posts,
                    serverhost=server_address)
            
        except Exception as error:
            sentence='ERROR1: '+error.__str__()
            return make_response(render_template('error.html',sentence=sentence))
    except Exception as error:
            sentence='ERROR2: '+error.__str__()
            return make_response(render_template('error.html',sentence=sentence))

# 管理者用アプリRegister，新規ユーザー追加
@app.route("/admin/register", methods=["GET","POST"])
def admin_register():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    user_prof=my_func.sql_ALLuser_profile(admin, adminpass)
    
    if my_func.admin_kakunin(admin, adminpass):
        pass
    else:
        sentence='初めからやり直してください。'
        return make_response(render_template('error.html',sentence=sentence))
    
    if len(admin)==0 or len(adminpass)==0:
        return 'NG1: cannot access'
    
    if request.args.get('status')=='first':
        try:    
            my_func.kakunin(admin, adminpass)
        except Exception as error:
            return 'NG: '+error.__str__()
        posts=[]
        resp = make_response(
                render_template(
                        'admin_register.html',
                        text='',
                        serverhost=server_address,
                        posts=posts,
                        year=datetime.datetime.now().year))
        
        return resp
    
    info={'newuser':request.form['newuser'],
          'newpass':request.form['newpass'],
          'rname':request.form['rname'],
          'type':request.form['type'],
          'org':request.form['org'],
          'year':request.form['year']}
    
    if len(request.form['newuser'])==0 or len(request.form['newpass'])==0 or \
        len(request.form['rname'])==0 or len(request.form['org'])==0:
        sentence='NG : Fill in the blank!: すべての空欄を埋めてください。'
        return make_response(render_template('error.html',sentence=sentence))
    
    if request.form['newuser'] in user_prof.keys():
        sentence='NG: 新しいユーザーを登録できません。ユーザー名[{}]は使われています。違うユーザー名を指定してください。'.format(request.form['newuser'])
        return make_response(render_template('error.html',sentence=sentence))
    
    try:
        hantei=my_func.adduser(admin, adminpass, info)
        if hantei:
            resp='OK'
            resp = make_response(render_template(
                    'admin_register.html',
                    text=request.form['rname']+'さんを登録しました．',
                    serverhost=server_address,
                    year=datetime.datetime.now().year)
            )
            #user_proの更新
            #user_prof=my_func.sql_ALLuser_profile(user_name, user_pass)
            return resp
        else:
            return 'NG'
    except Exception as error:
        return 'Fail:SQLserver Error'+error.__str__()

# 管理者用アプリ Message, 管理者から全体への連絡事項を追加
@app.route("/admin/message", methods=["GET","POST"])
def admin_message():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    user_prof=my_func.sql_ALLuser_profile(admin, adminpass)
    
    if my_func.admin_kakunin(admin, adminpass):
        pass
    else:
        return 'admin_kakunin error'
    
    messages = my_func.sql_message_get(
        admin,
        adminpass,
        max_messages = 10
    )
    
    posts = []
    for d in messages:
        posts.append({
            'day': d['day'],
            'rname': user_prof[d['userid']]['rname'],
            'group': d['group'],
            'title': d['title'],
            'contents': d['contents']}
        )
    
    if request.args.get('status')=='first':
        try:
            my_func.kakunin(admin, adminpass)
        except Exception as error:
            return 'NG: '+error.__str__()
        resp = make_response(
                render_template(
                        'admin_message.html',
                        serverhost=server_address,
                        posts=posts)
                )
        
        return resp
    
    try:
        if len(admin)==0 or len(adminpass)==0:
            return 'cannot access message'
        
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
                'day': d['day'],
                'rname': user_prof[d['userid']]['rname'],
                'group': d['group'],
                'title': d['title'],
                'contents': d['contents']}
            )
        
        return render_template(
                'admin_message.html', 
                 title='Message',
                 user=admin,
                 posts=posts,
                 serverhost=server_address
                 )
    except Exception as error:
        return error.__str__()

# 管理者用アプリAnalysis，簡単な統計，解析
@app.route("/admin/analysis", methods=["GET","POST"])
def admin_analysis():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    
    if my_func.admin_kakunin(admin, adminpass) and not(len(admin)==0 or len(adminpass)==0):
        pass
    else:
        sentence='初めからやり直してください。'
        return make_response(render_template('error.html',
                                             sentence=sentence))
    
    day_list=[]
    data_list=[]
    for i in range(31):
        day=datetime.date.today() - datetime.timedelta(days=i)
        strday=day.strftime("%Y-%m-%d")
        data=my_func.sql_data_per_day(strday)
        dassui_data=[100*float((d['wa']-d['wb'])/d['wb']) for d in data]
        day_list.append(day.strftime("%m/%d"))
        if i==0:
            today_list=dassui_data
        if len(dassui_data)>0:
            data_list.append(float(sum(dassui_data) / len(dassui_data)))
        else:
            data_list.append(float(-100))
    # 脱水率平均の図を出力
    data_list.reverse()
    day_list.reverse()
    
    plt.figure()
    plt.plot(data_list,'o')
    plt.xticks(range(0,31)[::3],day_list[::3])
    plt.grid(color='gray')
    plt.ylim(-2.5,1.5)
    plt.ylabel('Dehydration rate')
    plt.xlabel('Date')
    plt.title('Daily average')
    filename=datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'ave.png'
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
    filename2=datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'scatter.png'
    plt.savefig('./static/img/analysis/'+filename2)
    
    return make_response(render_template('admin_analysis.html',
                                         fname=filename,
                                         fname2=filename2))
# データのダウンロード
@app.route("/admin/download", methods=["GET","POST"])
def admin_download():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    
    if my_func.admin_kakunin(admin, adminpass) and not(len(admin)==0 or len(adminpass)==0):
        pass
    else:
        sentence='初めからやり直してください。'
        return make_response(render_template('error.html',
                                             sentence=sentence))
    resp = make_response()
    
    file=request.args.get('file')
    ## SQL####
    hantei=my_func.sql_makecsv(file)
    if hantei:
        pass
    else:
        sentence='ERROR: CSVファイルを作成できません。'
        return make_response(render_template('error.html',
                                             sentence=sentence))
    ## SQL####
    
    if file=='data':
        resp.data = open("./data.csv", "rb").read()
        downloadFileName = 'data.csv'    
        
    elif file=='user':
        resp.data = open("./user_list.csv", "rb").read()
        downloadFileName = 'user.csv'
    resp.headers['Content-Disposition'] = 'attachment; filename=' + downloadFileName
    resp.mimetype = 'text/csv'
    return resp

if __name__ == "__main__":
    app.run(debug=False,
            host=server_host,
            port=server_port,
            threaded=True)
