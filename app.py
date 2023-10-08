# -*- coding: utf-8 -*-
"""
部活Do!食べる部 Let's hydrate!
"""

from flask import Flask, render_template, make_response, redirect
import configparser
from login_app import login_app
from individual_app import individual_app
from management_app import management_app

app = Flask(__name__)

# サーバ環境ファイル読込み
config_ini = configparser.ConfigParser()
config_ini.read('../ENVFILE/config.ini', encoding='utf-8')
# サーバ情報設定
server_host    = config_ini['APP']['SERVER_HOST']
server_port    = config_ini['APP']['SERVER_PORT']

# ログイン画面
app.register_blueprint(login_app)
# 選手用画面
app.register_blueprint(individual_app)
# 管理者用画面
app.register_blueprint(management_app)

if __name__ == "__main__":
    app.run(debug = False,
            host = server_host,
            port = server_port,
            threaded = True)
