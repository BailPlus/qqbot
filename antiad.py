#Copyright Bail 2024
#antiad 反广告联合机器人 v1.0.1_2
#2024.8.19-2024.8.20

GROUPS = (434025815,)   # 要管理的群列表
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
        subtype = msg.get('subtype')
        gid = msg.get('group_id')
        if posttype == 'request':
            if reqtype == 'friend':
                print('检测到加人广告')
                blacklist(msg.get('user_id'),msg)
            elif (reqtype == 'group') and (subtype == 'invite') and (gid not in GROUPS):
                print('检测到拉人广告')
                blacklist(msg.get('user_id'),msg)
def blacklist(qq:int,msg):
    for i in GROUPS:
        api.sendg(ws,i,f'检测到广告: [CQ:at,qq={qq}]')
        print(msg)
        api.kick(ws,i,qq,False)
def main():
    recv()
    return 0

if __name__ == '__main__':
    main()
