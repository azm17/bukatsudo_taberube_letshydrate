#!/bin/bash

echo "アプリを起動します。"

python3 app.py > LOGFILE_APP.LOG 2>&1 &
echo "水分アプリを起動完了しました。"
python3 scheduler.py > LOGFILE_MAIL.LOG 2>&1 &
echo "メール配信システムを起動完了しました。"
