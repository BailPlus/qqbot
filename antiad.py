#Copyright Bail 2024
#antiad 反广告联合机器人 v1.0_1
#2024.8.19

GROUOS = (434025815,)   # 要管理的群列表
DATA = '/home/bail/git/qqbot/data'  # 机器人数据目录

import api_ws as api
import threading,json

ws = api.connect()
print('I; 已连接')

def recv():
    while True:
        msg:dict = json.loads(ws.recv())
        posttype = msg.get('post_type')
        reqtype = msg.get('request_type')
        if posttype == 'request':
            if reqtype == 'friend':
                print('检测到加人广告')
                blacklist(msg.get('user_id'))
            elif reqtype == 'group':
                print('检测到拉人广告')
                blacklist(msg.get('user_id'))
def blacklist(qq:int):
    for i in GROUOS:
        api.sendg(ws,i,f'检测到广告: [CQ:at,qq={qq}]')
        ##api.kick(ws,i,qq,True)
def main():
    recv()
    return 0

if __name__ == '__main__':
    main()
