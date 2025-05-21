#Copyright Bail 2025
#qqbot:offline_phone_notice 下线手机通知 v1.0_1
#2025.5.21

from typing import override
from liboffline_notice import OfflineHandler
import json,socket,sys,subprocess

class PhoneNoticeClient(OfflineHandler):
    def __init__(self):
        super().__init__()
        print('I: ws已连接')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(('...', ...))
        print('I: socket已连接')
    @override
    def handle(self, msg: dict):
        print(f'I: 已下线：{msg}')
        self.socket.send(msg.get('message','未知原因').encode()+b'\r\n')

def PhoneNoticeServer():
    while True:
        data = input()
        subprocess.run(['termux-notification','-t','QQBot Offline','-c',data],check=True)

if __name__ == '__main__':
    match sys.argv[1] if len(sys.argv) > 1 else None:
        case '-s':
            PhoneNoticeServer()
        case '-c':
            PhoneNoticeClient().run()
        case _:
            print('Usage: python3 offline_phone_notice.py [-s|-c]')
