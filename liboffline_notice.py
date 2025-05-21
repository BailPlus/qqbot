#Copyright Bail 2025
#qqbot:liboffline_notice 下线通知库 v1.0_1
#2025.5.21

from abc import ABC,abstractmethod
import json,api_ws as api

class OfflineHandler(ABC):
    """下线处理器"""
    def __init__(self):
        self.ws = api.connect()

    @abstractmethod
    def handle(self,msg:dict):
        """处理下线通知"""

    def run(self):
        """运行处理器"""
        while True:
            msg:dict = json.loads(self.ws.recv())
            if msg.get('post_type') != 'notice':
                continue
            if msg.get('notice_type') != "bot_offline":
                continue
            self.handle(msg)
