#Copyright Bail 2024
#qqbot:cqupt_jwzxnews_pusher 重邮教务在线通知推送器 v1.0_1
#2024.11.27

SUBSCRIBED_USERS = ()   # 已订阅通知的个人
SUBSCRIBED_GROUPS = ()    # 已订阅通知的群组
NEWS_URL = 'http://jwzx.cqupt.edu.cn/data/json_files.php?mdq4jDUd=oR0rgGlqEiwg.Vw6yzIfDd7QM.1xnuJsPD4tiWE5TYGQfAEdsYWGAcq2ShUAsk2bZzsMMA8azBKjllJNN1ye7pf95_ADLbh.qnVDF20pYFRkk5nyMik9vGA5dOHQQQchX1lV_s8kIK9'  # 通知获取链接
AI_URL = 'http://localhost:11434/api/generate'  # AI生成api

import api_ws,requests,sys,time

class News:
    def __init__(self,raw_data:dict):
        self.raw_data = raw_data
        self.id = raw_data['fileId']
        self.title = raw_data['title']
        self.publish_time = raw_data['pubTime']
        self.readcount = raw_data['readCount']
        self.publisher_name = raw_data['teaName']
    def __eq__(self, value) -> bool:
        return self.id == value.id
class Bot:
    def __init__(self,islazy:bool):
        self.news = self.get_news()
        self.ws = api_ws.connect()
        self.islazy = islazy
    def get_news(self)->dict:
        '''获取新闻动态'''
        newsjson = requests.get(NEWS_URL).json()
        # 检查是否为空
        if not newsjson['totalPage']:
            raise EmptyNewsError('获取新闻动态为空，请检查URL中mdq4jDUd字段是否正确！')
        # 新闻动态对象化
        news = []
        for i in newsjson['data']:
            news.append(News(i))
        return news
    def get_new_news(self)->dict:
        '''获取相较于上次获取新增的动态'''
        news = self.get_news()
        new_news = []
        for i in news:
            for j in self.news:
                if i == j:
                    break
            else:
                new_news.append(i)
        self.news = news
        return new_news
    def get_goodmorning_words(self)->str:
        '''通过调用本地AI获取早安问候语'''
        payload = {"stream":False,"model": "qwen2.5","prompt": "请使用一句话向同学们问早安，50字左右"}
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
            api_ws.sendu(self.ws,i,msg)
        for i in SUBSCRIBED_GROUPS:
            api_ws.sendg(self.ws,i,msg)
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
