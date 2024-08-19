import json,requests

URL = 'http://localhost:8089/'

def submit(url:str,data:dict,operate:str)->dict:
    res = json.loads(requests.get(URL+url,params=data).text)
    if res['status'] != 'ok':
        raise RuntimeError(f'{operate}失败:{res}')
    return res
def sendu(qq:int,msg:str)->dict:
    '''发送个人消息
qq:QQ号
msg:消息'''
    url = 'send_private_msg'
    data = {'user_id':qq,'message':msg}
    res = submit(url,data,'发送')
    return res
def sendg(qq:int,msg:str)->dict:
    '''发送个人消息
qq:群号
msg:消息'''
    url = 'send_group_msg'
    data = {'group_id':qq,'message':msg}
    res = submit(url,data,'发送')
    return res
def recall(msgid:int)->dict:
    '''撤回消息
msgid:消息号(见发送后的返回值)'''
    url = 'delete_msg'
    data = {'message_id':msgid}
    res = submit(url,data,'撤回')
    return res
def ban(gid:int,uid:int,t:int)->dict:
    '''单人禁言
uid:个人qq号
gid:群号
t:禁言时间(秒)，若为0则取消'''
    url = 'set_group_ban'
    data = {'group_id':gid,'user_id':uid,'duration':t}
    res = submit(url,data,'禁言')
    return res
def banall(gid:int,enable:bool=True)->dict:
    '''全员禁言
gid:群号
enable:是否禁言(False则取消)'''
    url = 'set_group_whole_ban'
    data = {'group_id':gid,'enable':enable}
    res = submit(url,data,'禁言')
    return res
def getulst()->dict:
    '''获取好友列表'''
    url = 'get_friend_list'
    res = submit(url,None,'获取')
    return res
def getmsg(mid:int)->dict:
    url = 'get_msg'
    data = {'message_id':mid}
    res = submit(url,data,'获取')
    return res
def getgroup(gid:int)->dict:
    url = 'get_group_info'
    data = {'group_id':gid}
    res = submit(url,data,'获取')
    return res
def kick(gid:int,uid:int,noreadd:bool=False):
    '''移出群成员
gid:群号
uid:要踢出的qq号
noreadd:拒绝重复加群请求'''
    url = 'set_group_kick'
    data = {'group_id':gid,'user_id':uid,'reject_add_request':noreadd}
    res = submit(url,data,'踢出')
    return res
