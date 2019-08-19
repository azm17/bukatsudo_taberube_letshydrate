# 脱水管理アプリケーション
## テストアプリケーション
herokuにアップしたテスト用のアプリはアクセスはこちら[一般ユーザー用](http://test-server0701.herokuapp.com/)
，[管理者用](http://test-server0701.herokuapp.com/admin)から体験できます．接続にはherokuのサーバーが一時停止していることがあるため時間がかかることがあります．

# 1. サーバーの導入方法
このアプリケーションサーバープログラム（server.pyおよびmy_function2_sql.py）は，Pythonのウェブアプリケーションフレームワーク Flaskをベースに作られており，それらに関するモジュールやその他のいくつかのモジュールをインストールする必要がある．例として，アプリケーションサーバーをUbuntu 18.04に導入する方法を記述していく．

#### サーバー情報
$ lsb_release -a  
No LSB modules are available.  
Distributor ID: Ubuntu  
Description:    Ubuntu 18.04.3 LTS  
Release:        18.04  
Codename:       bionic  
#### Pythonのバージョン
$ python3 -V  
Python 3.6.8  
#### 必要モジュール
- flask
- mysql-connector-python
- matplotlib

### 導入から実行まで
#### 1.リポジトリをクローン  
$ git clone https://github.com/azm17/bukatsudo_taberube_letshydrate.git  
#### 2.クローンしたディレクトリへ移動  
$ cd bukatsudo_taberube_letshydrate  
#### 3.必要モジュールの導入  
$ pip3 install flask  
$ pip3 install mysql-connector-python  
$ pip3 install matplotlib  

#### 4.導入済みのモジュールの確認  
$ pip3 freeze  
Click==7.0  
cycler==0.10.0  
Flask==1.1.1  
itsdangerous==1.1.0  
Jinja2==2.10.1  
kiwisolver==1.1.0  
MarkupSafe==1.1.1  
matplotlib==3.1.1  
mysql-connector-python==8.0.17  
numpy==1.17.0  
pkg-resources==0.0.0  
protobuf==3.9.1  
pyparsing==2.4.2  
python-dateutil==2.8.0  
six==1.12.0  
Werkzeug==0.15.5
#### 5.サーバーの設定  
##### server.py
プログラムファイルserver.pyで

###### 28行目
server_host='test-server0701.herokuapp.com'  
⇒
server_host='{グローバルIPまたは，URL}'  
###### 32行目
server_port=50000  
⇒
server_port='{server.pyを実行するサーバーのポート番号}'


に変更する．※プログラム中には{}は不要



##### my_function2_sql.py
プログラムファイルserver.pyで

SQLserver_host='192.168.0.32' ※SQLサーバーのホスト名(サーバーのプライベートIPアドレス)  
SQLserver_port=3306  ※SQLサーバーのポート番号

を適切なものに変更する．


#### 6.アプリケーションを実行
$ python3 server.py

# 2. 脱水管理アプリ開発計画
日付，天気，湿度，トレーニング，時間，運動前体重，運動後体重，飲水量をデータベースに保存し日々の脱水を管理する．開発用のリポジトリは[こちら](https://github.com/azm17/app0702)．
## 2.1. 機能
### 一般ユーザー向け
- 天気，湿度，トレーニング，時間，運動前体重，運動後体重，飲水量入力しデータベースに保存
- 過去の結果の一覧を表示
- 本日の結果
- 掲示板閲覧機能
- 今日の入力結果によってコメントを自動的に表示

### 管理ユーザー向け
- 最近の結果を表示
- 個別のユーザーの結果を表示
- 新規ユーザー登録
- 簡単な分析機能，平均，度数分布
- 掲示板登録機能
- 結果をCSV形式でダウンロード

## 2.2. 設計
ユーザー用，管理者用の画面はhtml,CSS,javascriptで作成し，アプリケーションサーバはPytholnのFlaskで作成する．データはMySQLで管理する．

## 2.3. データベース構成
### テーブル構成

#### テーブルuser_list (ユーザ情報)
|id|password|type|name|org|year|
|---|---|---|---|---|---|
|azumi|mamiya|su|間宮|shizuoka|2019|
|daiki|miyagawa|su|宮川|shizuoka|2019|
|kenshikn|kensin|ge|けんしん|shizuoka|2019|
|tomohiro|tsuchiya|ge|土屋|shizuoka|2019|

#### テーブルdata（トレーニング結果）
|id|day|weather|humidity|training|time|bweight|aweight|water|temp|rtime|  
|---|---|---|---|---|---|---|---|---|---|---|  
|azumi|2019-08-02|0|50|マラソン|2|70|68.9|0|30|201902191657|  
|daiki|2019-08-02|1|40|twitter|2|60|59.8|0.1|30|201902191667|  
|tomohiro|2019-08-02|2|30|ゲーム|2|55|54.9|0.3|30|201902191677|  
|azumi|2019-08-03|0|50|マラソン|2|70|68.9|0|30|201902191687|  
|daiki|2019-08-03|1|40|twitter|2|60|59.8|0.1|30|201902191697|  
|tomohiro|2019-08-03|2|30|ゲーム|2|55|54.9|0.3|30|201902191757|  

#### デーブルborad (掲示板)
|day|tolist|fromlist|title|contents|
|---|---|---|---|---|
|2019-08-11|ALL|azumi|名言|天才とは努力する凡才のことである．|
|2019-08-12|ALL|azumi|名言|今日は暑いですね．|

※ALLは全員へ