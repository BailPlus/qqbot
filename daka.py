JSON = 'data/daka.json'
DAKAED = 'data/dakaed.json'
LANSHAN_GID = 0
import api_ws as a
import random,json,time
w = a.connect()
with open(JSON) as file:
    dic = json.load(file)
with open(DAKAED) as file:
    dakaed = json.load(file)
while True:
    msg = json.loads(w.recv())
    posttype = msg.get('post_type')
    if posttype == 'message':
        msgtype = msg.get('message_type')
        uid = msg.get('user_id')
        gid = msg.get('group_id')
        text = msg.get('raw_message')
        msgid = msg.get('message_id')

        if msgtype == 'group' and gid == LANSHAN_GID:
            if text in ('试试手气','保底签到'):
                date = time.strftime('%Y%m%d')
                if uid in dakaed.get(date,[]):
                    a.sendg(w,gid,f'[CQ:at,qq={uid}] 你今天已经签过到了，明天再来吧')
                    continue
                else:
                    dakaed[date] = dakaed.get(date,[])+[uid]
                if text == '试试手气':
                    delta = random.randint(1,9)
                else:
                    delta = 5
                dic[str(uid)] = dic.get(str(uid),0)+delta
                with open(JSON,'w') as file:
                    json.dump(dic,file)
                with open(DAKAED,'w') as file:
                    json.dump(dakaed,file)
                a.sendg(w,gid,f'[CQ:at,qq={uid}] 签到成功，获得{delta}积分。')
            elif text == '排名':
                a.sendg(w,gid,'暂未开放')
            elif text == '导出签到数据':
                a.sendg(w,gid,json.dumps(dic,indent=4))
                a.sendg(w,gid,'注意，数据为新增积分，而不是总积分。')
                a.sendg(w,gid,json.dumps(dakaed))
                a.sendg(w,gid,'这是已签到人员')
