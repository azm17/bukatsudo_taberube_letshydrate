# -*- coding: utf-8 -*-
"""
部活Do!食べる部 Let's hydrate! ログイン画面
"""

from flask import Blueprint
from flask import Flask, request, render_template, make_response, redirect
import my_function2_sql as my_func
import configparser
import datetime
import hashlib

login_app = Blueprint("login_app", __name__)

# サーバ環境ファイル読込み
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')
# サーバ情報設定
server_address = config_ini['APP']['SERVER_ADDRESS']

# ログインフォーム
@login_app.route("/")
def entry():
    index = render_template('index.html', serverhost = server_address)
    
    resp = make_response(index)
    resp.set_cookie('user', '')
    resp.set_cookie('pass', '')
    return resp

# ユーザタイプ毎にリダイレクト
@login_app.route("/login", methods = ["POST"])
def login():
    # 入力情報（ID, PASSWORD）取得
    try:
        userid = request.form['user']
        userpass = hashlib.sha256(request.form['pass'].encode("utf-8")).hexdigest()
        print(hashlib.sha256("xxx".encode("utf-8")).hexdigest())
    except:
        userid = request.cookies.get('user')
        userpass = hashlib.sha256(request.cookies.get('pass').encode("utf-8")).hexdigest()
    
    # 入力情報DB問合せ
    user_prof = my_func.sql_get_user_profile(userid, userpass)
    
    # 情報一致なしのアカウント
    if len(user_prof) == 0:
        sentence = 'IDまたはパスワードが違います。正しい情報を入力してください。'
        redirect_to_index = render_template('error.html', sentence = sentence)
    # 利用停止中のアカウント
    elif user_prof[userid]['active_val'] == -1:
        sentence = 'あなたのアカウントは現在利用停止中です。'
        redirect_to_index = render_template('error.html', sentence = sentence)
    # 仮登録中のアカウント
    elif user_prof[userid]['active_val'] == 2:
        sentence = 'あなたのアカウントは仮登録状態です。本登録を完了させてください'
        redirect_to_index = render_template('error.html', sentence = sentence)
    # ユーザのタイプ毎にリダイレクト
    elif user_prof[userid]['type'] == 0 or user_prof[userid]['type'] == 2:# 管理者
        redirect_to_index = redirect('/admin/show', code=307)
        
    elif user_prof[userid]['type'] == 1:# 一般ユーザー
        redirect_to_index = redirect('/show', code=307)
    
    resp = make_response(redirect_to_index)
    resp.set_cookie('user', userid)
    resp.set_cookie('pass', userpass)
    return resp

# ユーザ登録画面
@login_app.route("/newaccount", methods = ["GET", "POST"])
def newaccount():
    text = ''
    org_dic = my_func.get_org_newaccount()
    if request.args.get('resgs') == 'user':
        # ユーザ登録処理
        info = {'newuser':request.form['newuser'],
                'newpass':hashlib.sha256(request.form['newpass'].encode("utf-8")).hexdigest(),
                'rname'  :request.form['rname'],
                'type'   :request.form['type'],
                'org'    :request.form['org'],
                'year'   :request.form['year'],
                'mail'   :request.form['mail'],
                'key'   :request.form['key']
                }
        
        if len(request.form['newuser']) == 0 or len(request.form['newpass']) == 0 or \
            len(request.form['rname']) == 0 or len(request.form['org']) == 0:
            
            sentence = 'エラー:すべての空欄を埋めてください。'
            index = render_template('error.html', sentence = sentence)
            return make_response(index)
        
        if my_func.sql_chk_userid(request.form['newuser']) == True:
            sentence = "エラー：ユーザ名[{}]は使用できません。".format(request.form['newuser'])
            index = render_template('error.html', sentence = sentence)
            return make_response(index)
        
        if my_func.sql_chk_toroku_key(request.form['org'],request.form['type'],request.form['key']) == False:
            sentence = "エラー：認証コードが違います。"
            index = render_template('error.html', sentence = sentence)
            return make_response(index)
        
        try:
            if my_func.adduser_general(info):
                text = request.form['rname'] + 'さんを仮登録しました。'
                
                try:
                    my_func.add_entry_tmp_account_mail(info, org_dic)
                    text = text + '仮登録メールが送信されます。仮登録メールから本登録を行ってください。'
                except Exception as error:
                    text = text + '仮登録が完了できませんでした。エラー内容：' + error.__str__()
                
                index = render_template('registered.html',
                            text = text,
                            serverhost = server_address,
                            newuser = info['newuser'],
                            newpass = "*****",
                            rname = info['rname'],
                            org = org_dic[info['org']]['org_name'],
                            year = info['year'],
                            mail  = info['mail'])
                resp = make_response(index)
                
                return resp
            else:
                return 'ユーザ登録に失敗しました。'
        except Exception as error:
            return 'Fail: SQL Server Error or mail error' + error.__str__()
    elif request.args.get('resgs') == 'hon':
        rtn_code = my_func.add_entry_complete_account_mail(request.args.get('userid'), request.args.get('tmpregisid'))
        if rtn_code != 0:
            return 'URLが無効です。'
        return '本登録完了しました。'
    
    else:
        # ユーザ登録フォーム送信
        posts_org = []
        
        for p in org_dic.keys():
            dic = {'org_id'  :p, 'org_name':org_dic[p]['org_name']}
            posts_org.append(dic)
        
        index = render_template('register.html',
                                text = text,
                                serverhost = server_address,
                                posts_org = posts_org,
                                year = datetime.datetime.now().year)
        
        resp = make_response(index)
        return resp