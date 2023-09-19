# -*- coding: utf-8 -*-
"""
部活Do!食べる部 Let's hydrate! 選手用画面
"""
from flask import Blueprint
from flask import Flask, request, render_template, make_response, redirect
import my_function2_sql as my_func
import configparser

individual_app = Blueprint("individual_app", __name__)

# サーバ環境ファイル読込み
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')
# サーバ情報設定
server_address = config_ini['APP']['SERVER_ADDRESS']

# 一般ユーザーの結果（表）画面
@individual_app.route("/show", methods = ["POST"])
def show():
    userid = request.cookies.get('user')
    userpass = request.cookies.get('pass')
    
    user_prof = my_func.sql_get_user_profile(userid,userpass)
    tenki_dic = my_func.init_tenki_dic()
    
    try:
        data = my_func.sql_data_get(userid)
        posts = []
        for d in reversed(data):
            neccessary1_tmp = max(round(float(d['wb'] * 0.01) + float(d['moi']), 1),0)
            
            posts.append({
                  'date'         :d['day'],# 日
                  'bweight'      :d['wb'],# 運動前体重
                  'aweight'      :d['wa'],# 運動後体重
                  'training'     :d['contents'][0:10],# トレーニング内容
                  'period'       :d['time'],# 運動時間
                  'intake'       :d['moi'],# 飲水量
                  'dehydraterate':my_func.dassui_ritu(d['wb'], d['wa']),# 脱水率
                  'tenki'        :str(tenki_dic[str(d['tenki'])]),# 天気
                  'shitsudo'     :d['shitsudo'],# 湿度
                  'temp'         :d['temp'],# 気温
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
                'rname'   :d['rname'],
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
            (detail:'''+error.__str__()+')'
        return make_response(render_template('error.html',
                                             sentence=sentence))

# Send entry form for data
@individual_app.route("/hello", methods = ["GET","POST"])
def hello():
    userid = request.cookies.get('user')
    userpass = request.cookies.get('pass')
    hantei = my_func.kakunin(userid,userpass)
    user_prof = my_func.sql_get_user_profile(userid,userpass)
    tenki_dic = my_func.init_tenki_dic()

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

# 結果入力
@individual_app.route("/enter", methods=["GET","POST"])
def enter():
    userid = request.cookies.get('user')
    userpass = request.cookies.get('pass')
    tenki_dic = my_func.init_tenki_dic()

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
        
        index = render_template('error.html',sentence = sentence)
        
        return make_response(index)
