import api

def main(data:dict):
    if data['post_type'] == 'message':
        sender = data['sender']['nickname']
        senderid = data['sender']['user_id']
        msgid = data['message_id']
        msg = data['message']
        if data['message_type'] == 'group': #判断群聊
            gid = data['group_id']
            sender = data['sender']['card']
            if sender == '':    #若群名片未设定则获取昵称
                sender = data['sender']['nickname']
            gname = api.getgroup(gid)['data']['group_name']
        print(f'┌{sender}({senderid}):[{msgid}]')
        if data['message_type'] == 'group':
            print(f'├从群聊:{gname}({gid})')
        print(f'└{msg}')
