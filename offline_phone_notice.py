#Copyright Bail 2025
#qqbot:offline_phone_notice 下线手机通知 v1.0_1
#2025.5.21

from typing import override
from liboffline_notice import OfflineHandler
import json,socket,sys,subprocess

class PhoneNoticeClient(OfflineHandler):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(('...', ...))
    @override
    def handle(self, msg: dict):
        self.socket.send(json.dumps(msg).encode()+b'\r\n')

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
