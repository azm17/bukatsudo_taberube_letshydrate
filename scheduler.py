import schedule
import time
import my_function_mail

def job():
    my_function_mail.send_mail()

schedule.every(1).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)  # 待ち