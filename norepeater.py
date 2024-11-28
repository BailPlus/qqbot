#Copyright Bail 2024
#qqbot:norepeater 打断复读机 v1.0_1
#2024.10.5

DOMAIN = ()
WINDOW_LENGTH = 0

import api_ws as api
import json

msg_queue = {}
conn = api.connect()

while True:
    msg = json.loads(conn.recv())
    posttype = msg.get('post_type')
    if posttype == 'message':
        msgtype = msg.get('message_type')
        uid = msg.get('user_id')
        gid = msg.get('group_id')
        text = msg.get('raw_message')
        msgid = msg.get('message_id')

        if msgtype != 'group' or gid not in DOMAIN:
            continue
        print(text)

        if gid not in msg_queue:
            msg_queue[gid] = [None]*WINDOW_LENGTH
            
        msg_queue[gid].pop(0)
        msg_queue[gid].append(text)

        # 排除火车
        if text == '[CQ:face,id=419]':
            continue

        for i in msg_queue[gid]:
            if i != text:
                break
        else:
            api.sendg(conn,gid,'嗯…打断复读机的事就交给我吧')
