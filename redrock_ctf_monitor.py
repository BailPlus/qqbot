#Copyright Bail 2024
#qqbot:redrock-ctf-monitor 红岩ctf看板器 v1.0_1
#2024.12.7

COOKIE = ''
URL = 'https://ctf.redrock.team/api/game/5/details'
UA = 'BailQqbot/0'
USERS = ()
GROUPS = ()
HELLO_WORD = '您的好友 红岩ctf看板器 已上线'

import requests,api_ws,time

class Info:
    def __init__(self,data:dict):
        self.raw_data = data
        self.challenge_cound = data['challengeCount']
class Monitor:
    functions = []
    def __init__(self,cookie:str,sleep_time:int|float=10):
        self.cookie = cookie
        self.sleep_time = sleep_time
        self.functions.extend((self.monitor_new_challenge,))
        self.ws = api_ws.connect()
        self.push(HELLO_WORD)
    def push(self,msg):
        msg = '[redrock-ctf-monitor]\n'+msg
        for i in USERS:
            api_ws.sendu(self.ws,i,msg)
        for i in GROUPS:
            api_ws.sendg(self.ws,i,msg)
    def getinfo(self)->Info:
        headers = {'User-Agent':UA,'Cookie':self.cookie}
        try:
            resp = requests.get(URL,headers=headers)
        except requests.exceptions.ConnectionError:
            self.push('日常掉线，已重新上线')
        # 请求错误处理
        if resp.status_code != 200:
            self.push(f'请求失败({resp.status_code}): {resp.json()}')
        # 处理信息
        info = Info(resp.json())
        return info
    def monitor_new_challenge(self,old_info:Info,new_info:Info):
        if old_info.challenge_cound < new_info.challenge_cound:
            self.push('上新题了，快来抢血！')
    def run(self):
        old_info = self.getinfo()
        while True:
            new_info = self.getinfo()
            for i in self.functions:
                i(old_info,new_info)
            old_info = new_info
            time.sleep(self.sleep_time)

if __name__ == '__main__':
    Monitor(COOKIE).run()
