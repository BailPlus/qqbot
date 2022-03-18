import sys,json,requests

URL = 'http://localhost:8089/'
me = 2915289604     #我的qq
xz = 749072911      #群“徐中金中”
why = 1195550334    #王昊雨qq
test = 110632907    #群“机器人测试群”
hlx = 1558614088    #黄联鑫qq
jqz = 2409407068    #靳骐榛qq

#基础类函数
def submit(url:str,data:dict)->dict:
    res = json.loads(requests.get(URL+url,params=data).text)
    return res
def printe(*args,**kw):
    print(*args,file=sys.stderr,**kw)

#实用类函数
def sendu(qq:int,msg:str)->dict:
    '''发送个人消息
qq:QQ号
msg:消息'''
    url = 'send_private_msg'
    data = {'user_id':qq,'message':msg}
    res = submit(url,data)
    if res['status'] == 'ok':
        msgid = res['data']['message_id']
        print(f'发送成功，消息号:{msgid}')
    else:
        printe(f'发送失败:{res}')
def sendg(qq:int,msg:str)->dict:
    '''发送个人消息
qq:群号
msg:消息'''
    url = 'send_group_msg'
    data = {'group_id':qq,'message':msg}
    res = submit(url,data)
    if res['status'] == 'ok':
        msgid = res['data']['message_id']
        print(f'发送成功，消息号:{msgid}')
    else:
        printe(f'发送失败:{res}')
def recall(msgid:int)->dict:
    '''撤回消息
msgid:消息号(见发送后的返回值)'''
    url = 'delete_msg'
    data = {'message_id':msgid}
    res = submit(url,data)
    if res['status'] == 'ok':
        print('已撤回，若>2min，可能不成功')
    else:
        printe(f'撤回失败:{res}')
def ban(uid:int,gid:int,t:int)->dict:
    '''单人禁言
uid:个人qq号
gid:群号
t:禁言时间(秒)，若为0则取消'''
    url = 'set_group_ban'
    data = {'group_id':gid,'user_id':uid,'duration':t}
    res = submit(url,data)
    if res['status'] == 'ok':
        print('已禁言')
    else:
        printe(f'操作失败:{res}')
def banall(gid:int,enable:bool=True)->dict:
    '''全员禁言
gid:群号
enable:是否禁言(False则取消)'''
    url = 'set_group_whole_ban'
    data = {'group_id':gid,'enable':enable}
    res = submit(url,data)
    if res['status'] == 'ok':
        if enable:
            print('已全员禁言')
        else:
            print('已解除全员禁言')
    else:
        printe(f'操作失败:{res}')
def getulst()->dict:
    '''获取好友列表'''
    url = 'get_friend_list'
    res = submit(url,None)
    if res['status'] == 'ok':
        print(res)
    else:
        printe(f'获取失败:{res}')
def getmsg(mid:int)->dict:
    url = 'get_msg'
    data = {'message_id':mid}
    res = submit(url,data)
    if res['status'] == 'ok':
        print(res)
    else:
        printe(f'获取失败:{res}')
def getgroup(gid:int)->dict:
    url = 'get_group_info'
    data = {'group_id':gid}
    res = submit(url,data)
    if res['status'] == 'ok':
        gname = res['group_name']
        gmemo = res['group_memo']
        print(f'群名称:{gname}\n群备注:{gmemo}')
    else:
        printe(f'获取失败:{res}')
