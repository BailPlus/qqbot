#Copyright Bail 2024
#qqbot:reat 艾特回复 v1.0_1
#2024.9.19

# 遇到单纯艾特就艾特回去，用于测试机器人是否可用

import api_ws as api,json

ws = api.connect()

while True:
    msg = json.loads(ws.recv())
    posttype = msg.get('post_type')
    if posttype == 'message':
        msgtype = msg.get('message_type')
        uid = msg.get('user_id')
        gid = msg.get('group_id')
        text = msg.get('raw_message')
        msgid = msg.get('message_id')

        if text.strip() == '[CQ:at,qq=3483498155]':
            api.sendg(ws,gid,f'[CQ:reply,id={msgid}][CQ:at,qq={uid}]')
