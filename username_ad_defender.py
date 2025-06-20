#Copyright Bail 2025
#qqbot:username_ad_defender 用户名广告拦截 v1.0_1
#2025.6.19

from typing import override
from enum import Enum
from abc import ABC,abstractmethod
from dataclasses import dataclass
import json, sqlite3, websocket, api_ws as api

BLACKLIST_WORDS = ['勤工', '学生会']    # 关键词黑名单
DOMAIN = [] # 作用域群组
DBNAME = 'username_ad_defender.db'  # 数据库文件名


@dataclass
class Message:
    class Type(Enum):
        DEFEND = False  # 需要判别广告的消息
        IGNORE = True   # 执行命令的消息

    gid:            int     # 群号
    uid:            int     # QQ号
    qqname:         str     # QQ昵称
    sender_role:    str     # 角色
    msgid:          int     # 消息号
    type:           Type    # 消息类型
    text:           str     # 消息


class MsgReceiver(ABC):
    @abstractmethod
    def recv(self) -> Message:
        """接收消息"""


class Judger(ABC):
    @abstractmethod
    def judge(self, msg: Message) -> bool:
        """判断是否为广告者"""


class DefendHandler(ABC):
    @abstractmethod
    def handle(self, msg:Message):
        """处理拦截"""


class IgnoreHandler(ABC):
    @abstractmethod
    def auth(self, msg: Message):
        """鉴权"""

    @abstractmethod
    def handle(self, msg: Message):
        """处理忽略"""


class Dao:
    conn: sqlite3.Connection

    def __init__(self):
        self.conn = sqlite3.connect(DBNAME)

    def create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS ignored_users (
                uid INTEGER PRIMARY KEY
            )
        ''')
        self.conn.commit()

    def is_ignored(self, uid: int) -> bool:
        return bool(
            self.conn.execute('''
                SELECT 1 FROM ignored_users WHERE uid = ?
            ''', (uid,))\
                .fetchone()
        )

    def add_ignore(self, uid: int):
        self.conn.execute('''
            INSERT OR IGNORE INTO ignored_users (uid) VALUES (?)
        ''', (uid,))
        self.conn.commit()

class DefaultReceiver(MsgReceiver):
    conn: websocket.WebSocket

    def __init__(self, ws: websocket.WebSocket):
        self.ws = ws

    @override
    def recv(self) -> Message:
        """接收消息"""
        msg = json.loads(self.conn.recv())
        if msg.get('post_type') != 'message':
            raise NotAMessage
        if msg.get('message_type') != 'group':
            raise NotAGroupMessage
        if msg.get('group_id') not in DOMAIN:
            raise GroupNotInDomain

        return Message(
            gid = msg.get('group_id'),
            uid = msg.get('user_id'),
            qqname = msg.get('sender').get('nickname'),
            sender_role = msg.get('sender').get('role'),
            msgid = msg.get('message_id'),
            type = msg.get('raw_message', '').startswith('/ignore'),
            text = msg.get('raw_message'),
        )


class DefaultJudger(Judger):
    ADMIN_ROLES = ['owner', 'admin']
    dao: Dao

    def __init__(self, dao: Dao):
        self.dao = dao

    @classmethod
    def is_admin(cls, msg: Message) -> bool:
        return msg.sender_role in cls.ADMIN_ROLES

    def is_in_ignore_list(self, msg: Message) -> bool:
        return self.dao.is_ignored(msg.uid)

    @override
    def judge(self, msg: Message) -> bool:
        if self.is_admin(msg) or self.is_in_ignore_list(msg):
            return False
        for i in BLACKLIST_WORDS:
            if i in msg.qqname:
                return True
        else:
            return False

class DefaultDefender(DefendHandler):
    def __init__(self, conn: websocket.WebSocket):
        self.conn = conn

    @override
    def handle(self, msg: Message) -> None:
        api.sendg(self.conn,msg.gid,f'[CQ:reply,id={msg.msgid}][CQ:at,qq={msg.uid}] 检测到你可能是广告。如有误报，请管理员发送 /ignore {msg.uid}')


class DefaultIgnoreHandler(IgnoreHandler):
    dao: Dao

    def __init__(self, dao: Dao):
        self.dao = dao

    @override
    def auth(self, msg: Message):
        return msg.sender_role in DefaultJudger.ADMIN_ROLES
    
    @override
    def handle(self, msg: Message):
        self.dao.add_ignore(msg.uid)


class IgnoreThisEvent(Exception):
    """忽略这个event"""

class NotAMessage(IgnoreThisEvent):
    """非消息"""

class NotAGroupMessage(IgnoreThisEvent):
    """非群消息"""

class GroupNotInDomain(IgnoreThisEvent):
    """群不在管辖范围"""


def main():
    conn = api.connect()
    dao = Dao()
    msg_receiver = DefaultReceiver(conn)
    judger = DefaultJudger(dao)
    defend_handler = DefaultDefender(conn)
    ignore_handler = DefaultIgnoreHandler(dao)

    while True:
        try:
            msg = msg_receiver.recv()
        except IgnoreThisEvent:
            continue
        if msg.type:    # 执行命令
            ignore_handler.handle(msg)
        elif judger.judge(msg):
            defend_handler.handle(msg)


if __name__ == '__main__':
    main()
