import subprocess
import my_function_mysql as my_func_sql

# メール送信機能
def send_mail():
    mail_dic = {}
    sql_query  = " SELECT MAIL_ID, MAIL_TO, MAIL_CC, MAIL_BCC, TITLE, CONTENT "
    sql_query += " FROM   TBL_MAIL"
    sql_query += " WHERE  FLG_SYORI = 0"
    rtn_query = my_func_sql.sql_run_query(sql_query)

    for row in rtn_query:
        cmd = 'echo "'+ row[5] + '" | mail -s "'+row[4]+'" -r info@taberube.jp ' 
        
        if row[2]!="" and row[2] is not None:
             cmd += " -c " + row[2]
        
        if row[3]!="" and row[3] is not None:
             cmd += " -b " + row[3]

        cmd += " " + row[1]
        cmd = 'echo "'+ row[5]
        result = subprocess.run(cmd, shell=True, capture_output=True)
        
        sql_query  = " UPDATE TBL_MAIL"
        sql_query += " SET    FLG_SYORI = 1 "
        sql_query += "      , UPD_YMD = CURRENT_DATE"
        sql_query += "      , UPD_TIME = CURRENT_TIME"
        if result.returncode == 0:
            sql_query += "      , FLG_SEND = 1 "
            sql_query += "      , SEND_YMD = CURRENT_DATE"
            sql_query += "      , SEND_TIME = CURRENT_TIME"
        sql_query += " WHERE  MAIL_ID  = " + str(row[0])
        sql_query += " AND    FLG_SYORI = 0"
        
        rtn_query = my_func_sql.sql_update_query(sql_query)

if __name__ == "__main__":
       send_mail()