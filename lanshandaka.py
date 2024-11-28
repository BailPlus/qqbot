LANSHAN_GID = 0
import api_ws as api
import time
while True:
    if time.strftime('%H%M') != '0000':
        time.sleep(1)
    else:
        break
w = api.connect()
api.sendg(w,LANSHAN_GID,'试试手气')
w.close()
