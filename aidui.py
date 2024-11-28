LANMEI_UID = 0
import api_ws as a
import random,json,time,requests
w = a.connect()
while True:
    msg = json.loads(w.recv())
    posttype = msg.get('post_type')
    if posttype == 'message':
        msgtype = msg.get('message_type')
        uid = msg.get('user_id')
        gid = msg.get('group_id')
        text = msg.get('raw_message')
        msgid = msg.get('message_id')

        if uid != LANMEI_UID:
            continue
        content = text
        print(f'收到消息: {content}')
        data = json.dumps({'model':'qwen2','stream':False,'prompt':content})
        response = json.loads(requests.post('http://localhost:11434/api/generate',data=data).text)['response']
        a.sendg(w,gid,f'[CQ:reply,id={msgid}] [CQ:at,qq={uid}] {response}')
