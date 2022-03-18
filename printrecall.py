import api

def main(data:dict):
    if (data['post_type'] == 'notice') and ('recall' in data['notice_type']):   #筛选报文:通知且撤回
        uid = data['user_id']                   #操作者qq号
        mid = data['message_id']                #被撤回消息号
        msgdic = api.getmsg(mid)['data']        #消息字典
        msg = msgdic['message']                 #消息内容
        sender = msgdic['sender']['nickname']   #发送者昵称
        senderid = msgdic['sender']['user_id']  #发送者QQ号
        if data['notice_type'] == 'group_recall':   #判断群聊
            uid = data['operator_id']           #操作者qq号
            gid = data['group_id']
            gname = api.getgroup(gid)['data']['group_name']
        print(f'┌{uid}撤回消息:[{mid}]')
        if data['notice_type'] == 'group_recall':   #判断群聊
            print(f'├发送者:{sender}({senderid})')
            print(f'├从群聊:{gname}({gid})')
        print(f'└{msg}')
