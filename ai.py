GIDS = ()
import api_ws as a
import random,json,time,requests
w = a.connect()
while True:
    msg = json.loads(w.recv())
##    print(msg)
    posttype = msg.get('post_type')
    if posttype == 'message':
        msgtype = msg.get('message_type')
        uid = msg.get('user_id')
        gid = msg.get('group_id')
        text = msg.get('raw_message')
        msgid = msg.get('message_id')

        if text[:38] != '[CQ:at,qq=3483498155,name=x_shine] ai ':
            continue
        content = text[38:]
        print(f'收到消息: {content}')
        if gid not in GIDS:
            print(f'非法的请求来源：{gid}')
            a.sendg(w,gid,f'[CQ:reply,id={msgid}] 403 Forbidden')
            continue
        data = json.dumps({'model':'qwen2','stream':False,'prompt':content})
        try:
            response = json.loads(requests.post('http://localhost:11434/api/generate',data=data).text)['response']
        except requests.exceptions.ConnectionError:
            print('AI服务器离线')
            a.sendg(w,gid,f'[CQ:reply,id={msgid}] 503 Service Unavailable')
        except json.decoder.JSONDecodeError:
            print('AI服务器响应错误')
            a.sendg(w,gid,f'[CQ:reply,id={msgid}] 500 Internal Server Error')
        else:
            a.sendg(w,gid,f'[CQ:reply,id={msgid}] [CQ:at,qq={uid}] {response}')
