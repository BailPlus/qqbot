#Copyright Bail 2024
#qqbot:cqupt_add_group_check 重邮加群请求处理 v1.0_1
#2024.10.6

DOMAIN = ()

import api_ws as api,json,libredrock_api

ws = api.connect()

while True:
    # 过滤事件并获取信息
    event = json.loads(ws.recv())
    if (event.get('post_type') != 'request') or (event.get('request_type') != 'group') or (event.get('sub_type') != 'add'):
        continue
    print(event)
    gid = event.get('group_id')
    if gid not in DOMAIN:
        continue
    flag = event.get('flag')
    comment = event.get('comment')

    # 去除非规范填写
    try:
        name,stuid,authcode = comment.split('\n')[1][3:].split(' ')    # comment第二行从第四个字符开始，用空格隔开
    except Exception:
        api.set_group_add_request(ws,flag,'add',False,'格式错误，请重新填写')
        continue

    # 验证身份
    result,msg = libredrock_api.check(name,stuid,authcode)
    api.set_group_add_request(ws,flag,'add',result,msg)
