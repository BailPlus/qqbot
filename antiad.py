#Copyright Bail 2024
#antiad 反广告联合机器人 v1.1_3
#2024.8.19-2024.8.20

GROUPS = ()   # 要管理的群列表
NOOPERATORS = ()    # 屏蔽者，也就是滥用手动移除的人
DATA = '/home/bail/git/qqbot/data'  # 机器人数据目录

import api_ws as api
import threading,json,os

ws = api.connect()
print('I: 已连接')

def recv():
    while True:
        msg:dict = json.loads(ws.recv())
        posttype = msg.get('post_type')
        # 主动检测：被添加或被拉群
        if posttype == 'request':
            reqtype = msg.get('request_type')
            subtype = msg.get('subtype')
            gid = msg.get('group_id')
            if reqtype == 'friend':
                print('检测到加人广告')
                aderqq = msg.get('user_id')
                blacklist(aderqq,f'检测到加人广告: [CQ:at,qq={aderqq}]')
            elif (reqtype == 'group') and (subtype == 'invite') and (gid not in GROUPS):
                print('检测到拉人广告')
                aderqq = msg.get('user_id')
                blacklist(aderqq,f'检测到拉人广告: [CQ:at,qq={aderqq}]')
        # 被动触发：管理群内被管理人员@并附带广告人员qq号
        if posttype == 'message':
            msgtype = msg.get('message_type')
            uid = msg.get('user_id')
            gid = msg.get('group_id')
            text = msg.get('raw_message')
            msgid = msg.get('message_id')
            sender_role = msg.get('sender').get('role')
            if (msgtype == 'group') \
              and (gid in GROUPS) \
              and (f'[CQ:at,qq={msg.get("self_id")}' in text):  # 在管理群内被@
                msgcut = text.split()
                if msgcut[1] == 'kick': # kick指令
                    if sender_role in ('owner','admin'):    # 如果是管理层则执行操作
                        aderqq = int(msgcut[2])
                        blacklist(aderqq)
                    else:   # 如果是普通成员
                        api.sendg(ws,gid,f'[CQ:reply,id={msgid}] Permission denied')
                elif msgcut[1] == 'sudo' and msgcut[2] == 'kick':   # 彩蛋: sudo kick指令
                    if sender_role in ('owner','admin'):    # 如果是管理层则执行操作
                        aderqq = int(msgcut[2])
                        blacklist(aderqq)
                    else:
                        api.sendg(ws,gid,f'[CQ:reply,id={msgid}] [CQ:at,qq={uid}] is not in the sudoers file. This incident won\'t be reported.')
        print(msg)
def blacklist(qq:int,msg):
    for i in GROUPS:
        api.sendg(ws,i,f'已移除[CQ:at,qq={qq}]')
        api.kick(ws,i,qq,False)
def main():
    recv()
    return 0

if __name__ == '__main__':
    main()
