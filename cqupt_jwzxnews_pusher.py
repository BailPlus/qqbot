#Copyright Bail 2024-2025
#qqbot:cqupt_jwzxnews_pusher 重邮教务在线通知推送器 v1.1_2
#2024.11.27-2025.5.21

SUBSCRIBED_USERS = ()   # 已订阅通知的个人
SUBSCRIBED_GROUPS = ()    # 已订阅通知的群组
NEWS_URL = 'http://jwzx.cqupt.edu.cn/data/json_files.php?mdq4jDUd=oR0rgGlqEiwg.Vw6yzIfDd7QM.1xnuJsPD4tiWE5TYGQfAEdsYWGAcq2ShUAsk2bZzsMMA8azBKjllJNN1ye7pf95_ADLbh.qnVDF20pYFRkk5nyMik9vGA5dOHQQQchX1lV_s8kIK9'  # 通知获取链接
AI_URL = 'http://localhost:11434/api/generate'  # AI生成api
UA = 'BailQqbot/0'
NEWS_FILE = 'news.json'  # 通知列表文件

from dataclasses import dataclass
import api_http,requests,sys,time,json,os

@dataclass(frozen=True)
class News:
    '''教务在线通知类'''
    raw_data:       dict
    id:             str
    title:          str
    publish_time:   str
    readcount:      int
    publisher_name: str

    @classmethod
    def from_json(cls,raw_data:dict):
        return cls(
            raw_data=raw_data,
            id=raw_data['fileId'],
            title=raw_data['title'],
            publish_time=raw_data['pubTime'],
            readcount=raw_data['readCount'],
            publisher_name=raw_data['teaName']
        )

    def __eq__(self, value) -> bool:
        return self.id == value.id

    def __hash__(self) -> int:
        return hash(self.id)
    
class Bot:
    islazy:bool

    def __init__(self,islazy:bool):
        self.islazy = islazy
        if not os.path.exists(NEWS_FILE):
            # 如果没有通知列表文件，则创建一个空的通知列表
            with open(NEWS_FILE,'w',encoding='utf-8') as f:
                f.write('[]')

    @property
    def news(self)->list[News]:
        '''获取当前的通知列表'''
        with open(NEWS_FILE,'r',encoding='utf-8') as f:
            news = json.load(f)
        # 将通知列表对象化
        return [News.from_json(i) for i in news]

    @news.setter
    def news(self,value:list[News]):
        '''设置当前的通知列表'''
        # 将当前通知列表保存到文件中
        with open(NEWS_FILE,'w',encoding='utf-8') as f:
            json.dump([i.raw_data for i in value],f,ensure_ascii=False,indent=2)

    def get_news(self)->list[News]:
        '''获取新闻动态'''
        newsjson = requests.get(NEWS_URL, headers={'User-Agent': UA}).json()
        # 检查是否为空
        if not newsjson['totalPage']:
            raise EmptyNewsError('获取新闻动态为空，请检查URL中mdq4jDUd字段是否正确！')
        # 新闻动态对象化
        return [News.from_json(i) for i in newsjson['data']]

    def get_new_news(self)->list[News]:
        '''获取相较于上次获取新增的动态'''
        news = self.get_news()
        new_news = [i for i in news if i not in self.news]
        self.news = new_news
        return new_news

    def get_goodmorning_words(self)->str:
        '''通过调用本地AI获取早安问候语'''
        # TODO: 改成使用ollama sdk进行调用
        payload = {"stream":False,"model": "qwen3","prompt": "请使用一句话向同学们问早安，50字左右"}
        words = requests.post(AI_URL,json=payload).json().get('response','早上好喵~')
        return words

    def construct_post_text(self,news:list[News]):
        '''构造推文'''
        texts = []
        texts.append(time.strftime('今天是%m.%d'))
        texts.append(self.get_goodmorning_words())
        if news:
            texts.append('最新教务通知：')
            for i,j in enumerate(news):
                texts.append(f'{i+1}. {j.title} ( http://jwzx.cqupt.edu.cn/fileShowContent.php?id={j.id} )')
        else:
            texts.append('教务在线没有新通知哦~')
        return '\n'.join(texts)

    def publish_new_news(self,msg:str):
        '''向订阅用户和群组推送推文'''
        for i in SUBSCRIBED_USERS:
            api_http.sendu(i,msg)
        for i in SUBSCRIBED_GROUPS:
            api_http.sendg(i,msg)

class EmptyNewsError(ValueError):
    '''获取教务在线通知为空'''
    def __init__(self,t:str):
        self.t = t
    def __str__(self):
        return self.t

def main():
    islazy = '--lazy' in sys.argv
    bot = Bot(islazy)
    isnow = '--now' in sys.argv
    if isnow:
        new_news = bot.get_new_news()
        msg = bot.construct_post_text(new_news)
        bot.publish_new_news(msg)
        return
    while True:
        if time.strftime('%H') != '07':
            time.sleep(1800)
            continue
        new_news = bot.get_new_news()
        if not bot.islazy or new_news:
            msg = bot.construct_post_text(new_news)
            bot.publish_new_news(msg)
        time.sleep(3600)

if __name__ == '__main__':
    sys.exit(main())
