import subprocess

def send_mail_newaccount(info,org_dic):
    title = '【部活Do!食べる部 Let\'s hydrate！】新規ユーザー登録完了通知'
    
    content = '\{rname}さん、'\
           +'部活Do!食べる部 Let\'s hydrate！のご利用ありがとうございます。\n'\
           +'新規ユーザーの登録が完了しましたので、登録情報を通知します。\n'\
           +'    【登録情報】\n'\
           +'\tユーザー名：{newuser}\n'\
           +'\tパスワード：{newpass}\n'\
           +'\t名前：{rname}\n'\
           +'\t組織：{org_name}\n'\
           +'\t入学年度：{year}\n'\
           +'\tメールアドレス：{mail}\n'\
           +'\n\n'\
           +'※もしメールに心当たりがない場合は誰かがあなたのパスワードを変更しようとした恐れがあります。\n'\
           +'\n\n\n'\
           +'----------\n'\
           +'発行: 部活Do!食べる部 Let\'s hydrate！ '\
           +'COPYRIGHT © taberube.jp ALL RIGHTS RESERVED.'
    
    content=content.format(newuser=info['newuser'], 
                            newpass=info['newpass'], 
                            rname=info['rname'],
                            org_name=org_dic[info['org']]['org_name'],
                            year=info['year'],
                            mail=info['mail'])
    
    cmd = 'echo "'+ content + '" | mail -s "'+title+'" -r info@taberube.jp ' + info['mail']
    subprocess.run(cmd, shell=True)