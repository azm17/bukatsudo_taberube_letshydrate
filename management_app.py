from flask import Blueprint
from flask import Flask, request, render_template, make_response, redirect
import my_function2_sql as my_func
import configparser
import datetime
import matplotlib.pyplot as plt
import os
import glob
import hashlib

management_app = Blueprint("management_app", __name__)

# サーバ環境ファイル読込み
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')
# サーバ情報設定
server_address = config_ini['APP']['SERVER_ADDRESS']

# 管理者mainページ
@management_app.route("/admin/show", methods = ["POST"])
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
@management_app.route("/admin/watch", methods = ["POST"])
def admin_watch():# ユーザリスト　ユーザを選び -> admin_watch_show()
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    
    try:
        user_prof = my_func.sql_ALLuser_profile(admin,adminpass)
        
    except Exception as error:
        sentence = 'ユーザ情報取得に失敗しました。\n{}'.format(error.__str__())
        index = render_template('error.html', sentence = sentence)
        resp = make_response(index)
    
    posts = []; posts_admin = [] 
    posts_coach = []; posts_unusable = []
    
    for name in user_prof.keys():
        dic = {'name'     :user_prof[name]['rname'],
                'org'     :user_prof[name]['org_name'],
                'year'    :user_prof[name]['year'],
                'id'      :name,
                'keyword' :str(user_prof[name]['year']) \
                     + user_prof[name]['org'] + name,
               }
        if user_prof[admin]['type'] == 2 \
            and dic['org'] == user_prof[admin]['org_name']:
            
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
@management_app.route("/admin/watch/show", methods = ["GET", "POST"])
def admin_watch_show():
    admin = request.cookies.get('user')# クッキーを保存
    adminpass = request.cookies.get('pass')# クッキーを保存
    tenki_dic = my_func.init_tenki_dic()

    try:
        user_prof = my_func.sql_ALLuser_profile(admin,adminpass)
        uid_get = request.args.get('name')#　見たいユーザ名
        real_name = user_prof[uid_get]['rname']# ユーザの本名
        
        data = my_func.sql_data_get(uid_get)
        posts = []
        for d in reversed(data):# dataは辞書形式
            neccessary1_tmp = max(round(float(d['wb']*0.01) + float(d['moi']), 1),0)

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
              'shitsudo'      :d['shitsudo'],#湿度
              'temp'          :d['temp'],
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
        index = render_template('error.html', sentence = sentence)
        return make_response(index)


# 管理者用アプリNew!(過去2日の投稿を表示)
@management_app.route("/admin/latest", methods = ["POST"])
def admin_latest():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    tenki_dic = my_func.init_tenki_dic()

    if admin == '' or adminpass == '':
        sentence = 'ログアウトしています。'
        index = render_template('error.html',
                                sentence = sentence)
        return make_response(index)
    
    if not (my_func.admin_coach_kakunin(admin, adminpass)):
        sentence = '初めからやり直してください。'
        index = render_template('error.html', sentence = sentence)
        return make_response(index)
    
    try:
        user_prof = my_func.sql_ALLuser_profile(admin,adminpass)
        try:
            data = my_func.sql_data_get_latest_all(admin,adminpass)
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
@management_app.route("/admin/register",
           methods = ["GET", "POST"])
def admin_register():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    text = ''
    
    if not (my_func.admin_kakunin(admin, adminpass)):
        sentence = '機能制限： ユーザー管理機能は管理者のみ利用可能です。'
        index = render_template('error.html', sentence = sentence)
        return make_response(index)
    
    if request.args.get('resgs') == 'org':
        if len(request.form['org_id']) == 0 \
            or len(request.form['org_name']) == 0:
            sentence = 'ERROR : Fill in the blank!: すべての空欄を埋めてください。'
            index = render_template('error.html', sentence = sentence)
            return make_response(index)
        
        if len(request.form['org_id']) !=3:
            sentence = '組織IDは3文字で入力してください。'
            index = render_template('error.html', sentence = sentence)
            return make_response(index)
        
        if request.form['org_id'] in my_func.get_org().keys():
            sentence = '''
                        NG: 新しい組織を登録できません。
                        組織ID[{}]は使われています。違う組織名を指定してください。
                        '''.format(request.form['org_id'])
            index = render_template('error.html',sentence = sentence)
            return make_response(index)
        
        try:
            info = {'org_id':request.form['org_id'],
                    'org_name':request.form['org_name'],
                    'key_player':request.form['key_player'],
                    'key_staff':request.form['key_staff']}
            my_func.addorg(admin, adminpass, info)
            
        except Exception as error:
            sentence = 'ERROR: ' + error.__str__()
            index = render_template('error.html',sentence = sentence)
            return make_response(index)
    
    if request.args.get('resgs') == 'user':
        # ユーザーの登録
        info = {'newuser':request.form['newuser'],
                'newpass':hashlib.sha256(request.form['newpass'].encode("utf-8")).hexdigest(),
                'rname'  :request.form['rname'],
                'type'   :request.form['type'],
                'org'    :request.form['org'],
                'year'   :request.form['year']
                }
        
        if len(request.form['newuser']) == 0 or len(request.form['newpass']) == 0 or \
            len(request.form['rname']) == 0 or len(request.form['org']) == 0:
            
            sentence = 'ERROR : Fill in the blank!: すべての空欄を埋めてください。'
            index = render_template('error.html',sentence = sentence)
            return make_response(index)
        
        if request.form['newuser'] in my_func.sql_ALLuser_profile(admin,adminpass).keys():
            sentence = '''
                        NG: 新しいユーザーを登録できません。
                        ユーザー名[{}]は使われています。違うユーザー名を指定してください。
                        '''.format(request.form['newuser'])
            index = render_template('error.html', sentence = sentence)
            return make_response(index)
        
        try:
            if my_func.adduser(admin, adminpass, info):
                text = request.form['rname'] + 'さんを登録しました．',

            else:
                return 'NG'
        except Exception as error:
            return 'Fail: SQL Server Error' + error.__str__()
    
    user_prof = my_func.sql_ALLuser_profile(admin,adminpass)
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

@management_app.route("/admin/account", methods = ["GET","POST"])
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
@management_app.route("/admin/message", methods = ["GET", "POST"])
def admin_message():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    org_list = my_func.get_org2(admin,adminpass)

    messages = my_func.sql_message_get(
        admin,
        adminpass,
        max_messages = 100
    )
    
    posts = []
    for d in messages:
        posts.append({
            'day'     :d['day'],
            'rname'   :d['rname'],
            'group'   :d['group'],
            'title'   :d['title'],
            'contents':d['contents']}
        )
    
    if request.args.get('status') == 'first':
        index = render_template('admin_message.html',
                                serverhost = server_address,
                                posts = posts,
                                org_list = org_list)
        resp = make_response(index)
        return resp
    
    try:
        group = str(request.form['org'])
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
                max_messages = 100
                )
        
        posts = []
        for d in messages:
            posts.append({
                'day'     :d['day'],
                'rname'   :d['rname'],
                'group'   :d['group'],
                'title'   :d['title'],
                'contents':d['contents']}
            )
        
        return render_template(
                'admin_message.html', 
                 title = 'Message',
                 user = admin,
                 posts = posts,
                 org_list = org_list,
                 serverhost = server_address
                 )
    except Exception as error:
        return error.__str__()

# 管理者用アプリAnalysis，簡単な統計，解析
@management_app.route("/admin/analysis", methods = ["GET","POST"])
def admin_analysis():
    return '調整中です。'
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    
    if my_func.admin_coach_kakunin(admin, adminpass) \
        and not(len(admin) == 0 or len(adminpass) == 0):
        pass
    else:
        sentence = '初めからやり直してください。'
        index = render_template('error.html', sentence = sentence)
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
@management_app.route("/admin/download", methods=["GET","POST"])
def admin_download():
    admin = request.cookies.get('user')
    adminpass = request.cookies.get('pass')
    resp = make_response()
    
    file = request.args.get('file')
    name = request.args.get('name')
    ## SQL####
    try:
        my_func.sql_makecsv(file, name,admin,adminpass)
    except Exception as error:
        sentence = 'ERROR: CSVファイルを作成できません。' + error.__str__()
        index = render_template('error.html', sentence = sentence)
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
