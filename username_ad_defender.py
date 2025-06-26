#Copyright Bail 2025
#qqbot:username_ad_defender 用户名广告拦截 v1.0_1
#2025.6.19

from __future__ import annotations
tokenizer = None
from typing import override
from enum import Enum
from abc import ABC,abstractmethod
from dataclasses import dataclass
from ad_defender.predict import predict, tokenizer
import json, sqlite3, time, websocket, api_ws as api

BLACKLIST_WORDS = ['勤工', '学生会']    # 关键词黑名单
DOMAIN = [] # 作用域群组
DBNAME = 'username_ad_defender.db'  # 数据库文件名
MSGLIMIT = 5    # 一分钟最多发送的消息数


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

    def reply(self, msg: str) -> Message:
        return self.to_send(
            gid=self.gid,
            text=f'[CQ:reply,id={self.msgid}][CQ:at,qq={self.uid}] ' + msg
        )
    
    @classmethod
    def to_send(cls, gid: int, text: str) -> Message:
        return cls(
            gid=gid,
            uid=0,
            qqname='',
            sender_role='',
            msgid=0,
            type=None, # type: ignore
            text=text
        )


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


class MessageSender(ABC):
    @abstractmethod
    def send(self, msg: Message):
        """发送消息"""


class Dao:
    conn: sqlite3.Connection

    def __init__(self):
        self.conn = sqlite3.connect(DBNAME)
        self.create_table()

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
    ws: websocket.WebSocket

    def __init__(self, ws: websocket.WebSocket):
        self.ws = ws

    @override
    def recv(self) -> Message:
        """接收消息"""
        msg = json.loads(self.ws.recv())
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

class AiContentJudger(DefaultJudger):
    @override
    def judge(self, msg: Message) -> bool:
        tokenizer #type: ignore # 用于使编辑器认为已经使用了jieba
        if self.is_admin(msg) or self.is_in_ignore_list(msg):
            return False
        result = predict(msg.text)
        print(msg.text, result)
        return result

class DefaultDefender(DefendHandler):
    conn: websocket.WebSocket
    message_sender: MessageSender

    def __init__(self, conn: websocket.WebSocket, message_sender: MessageSender):
        self.conn = conn
        self.message_sender = message_sender

    @override
    def handle(self, msg: Message):
        self.message_sender.send(
            msg.reply(f'检测到你可能是广告。如有误报，请管理员发送 /ignore {msg.uid}')
        )


class DefaultIgnoreHandler(IgnoreHandler):
    dao: Dao
    ws: websocket.WebSocket
    message_sender: MessageSender

    def __init__(self, dao: Dao, ws: websocket.WebSocket, message_sender: MessageSender):
        self.dao = dao
        self.ws = ws
        self.message_sender = message_sender

    def reply(self, msg: Message, text: str):
        self.message_sender.send(
            msg.reply(text)
        )

    @override
    def auth(self, msg: Message):
        return msg.sender_role in DefaultJudger.ADMIN_ROLES
    
    @override
    def handle(self, msg: Message):
        if not self.auth(msg):
            api.sendg(self.ws, msg.gid, '权限不足')
            return

        try:
            qq_uid_str = msg.text.split()[1]
        except IndexError:
            self.reply(msg, '命令语法不正确。格式为：/ignore <QQ号>')
            return
        try:
            qq_uid = int(qq_uid_str)
        except ValueError:
            self.reply(msg, 'QQ号不正确')
            return
        try:
            self.dao.add_ignore(qq_uid)
        except Exception:
            self.reply(msg, '添加失败')
        else:
            self.reply(msg, f'已将{qq_uid}添加至白名单')


class DefaultSender(MessageSender):
    ws: websocket.WebSocket # ws连接

    def __init__(self, ws: websocket.WebSocket):
        self.ws = ws
    
    @override
    def send(self, message: Message):
        api.sendg(self.ws, message.gid, message.text)


class LimitedSender(DefaultSender):
    """有限流的发送器"""
    minute: int     # 分钟戳
    msgnum: int     # 当前分钟的消息数
    limitation: int # 一分钟最多发送的消息数量

    def __init__(self, ws: websocket.WebSocket, limitation: int):
        super().__init__(ws)
        self.minute = self.get_minute()
        self.msgnum = 0
        self.limitation = limitation

    @staticmethod
    def get_minute() -> int:
        return int(
            time.time() // 60
        )

    def check_limitation(self):
        now_minute = self.get_minute()
        if now_minute != self.minute:
            self.msgnum = 0
            return
        if self.msgnum >= self.limitation:
            raise MessageFrequenceLimitationExceed
        self.msgnum += 1

    @override
    def send(self, message: Message, ignore_exceed: bool = True):
        try:
            self.check_limitation()
        except MessageFrequenceLimitationExceed:
            if not ignore_exceed:
                raise
        else:
            super().send(message)


class IgnoreThisEvent(Exception):
    """忽略这个event"""

class NotAMessage(IgnoreThisEvent):
    """非消息"""

class NotAGroupMessage(IgnoreThisEvent):
    """非群消息"""

class GroupNotInDomain(IgnoreThisEvent):
    """群不在管辖范围"""

class MessageFrequenceLimitationExceed(Exception):
    """消息频率超出限制"""

def main():
    conn = api.connect()
    dao = Dao()
    msg_receiver = DefaultReceiver(conn)
    judger = AiContentJudger(dao)
    message_sender = LimitedSender(conn, MSGLIMIT)
    defend_handler = DefaultDefender(conn, message_sender)
    ignore_handler = DefaultIgnoreHandler(dao, conn, message_sender)

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
