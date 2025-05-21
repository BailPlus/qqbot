#Copyright Bail 2024
#qqbot:duty_notify 值日通知 v1.1_2
#2024.9.19-2024.9.30

GID = 0
DUTIERS = ()
OFFSET = 0

import api_http as api,time,sys

def getdutier():
    datestamp = (time.time()+28800)//86400
    index = int((datestamp+OFFSET) % len(DUTIERS))
    return DUTIERS[index]

def push_dutier():
    dutier = getdutier()
    ##    print(dutier)
    api.sendg(GID,f'今天轮[CQ:at,qq={dutier}]值日')

def main():
    while True:
        if '--now' in sys.argv:
            push_dutier()
            exit()
        while True:
            h,m = map(int,time.strftime('%H:%M').split(':'))
            print(f'{h}:{m}')
            if h == 6 and m == 0:
                print('Time is up!')
                break
            elif h == 5:
                if 0<=m<50:
                    print('sleep 5min')
                    time.sleep(300)
                elif 50<=m<58:
                    print('sleep 1min')
                    time.sleep(60)
                else:
                    print('sleep 1s')
                    time.sleep(1)
            else:
                print('sleep 1h')
                time.sleep(3600)
        push_dutier()
        time.sleep(300)

if __name__ == '__main__':
    main()
