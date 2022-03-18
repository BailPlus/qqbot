import libkeyword,api

@libkeyword.exist(('淘宝',))
def taobao(msg:dict):
    if data['message_type'] == 'group': #判断群聊
        gid = data['group_id']
    uid = data['sender']['user_id']
    api.sendg(gid,f'[CQ:at,qq={uid}] 检测到你发送广告，将被踢出')
    api.kick(gid,uid)
@libkeyword.exist(('加群','加入','群号','二维码'))
def addgroup(msg:dict):
    if data['message_type'] == 'group': #判断群聊
        gid = data['group_id']
    uid = data['sender']['user_id']
    api.sendg(gid,f'[CQ:at,qq={uid}] 检测到你发送广告，警告1次')
    api.ban(gid,uid,3600)

def main(_):
    pass
