#Copyright Bail 2024-2025
#qqbot:cqupt_jwzxnews_pusher 重邮教务在线通知推送器 v1.2_3
#2024.11.27-2025.7.11

from dataclasses import dataclass
from abc import ABC,abstractmethod
from bs4 import BeautifulSoup, Tag
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
import api_http,requests,sys,time,json,os

SUBSCRIBED_USERS = ()   # 已订阅通知的个人
SUBSCRIBED_GROUPS = ()    # 已订阅通知的群组
NEWS_URL = 'https://jw.cqupt.edu.cn/tzgg.htm'  # 通知获取链接
AI_URL = 'http://localhost:11434/api/generate'  # AI生成api
UA = 'BailQqbot/0'
NEWS_FILE = 'news.json'  # 通知列表文件
FIREFOX_DRIVER_PATH = 'geckodriver'


# ===== 数据模型 =====
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
    def from_json(cls,raw_data:dict) -> 'News':
        return cls(
            raw_data=raw_data,
            id=raw_data['fileId'],
            title=raw_data['title'],
            publish_time=raw_data['pubTime'],
            readcount=raw_data['readCount'],
            publisher_name=raw_data['teaName']
        )

    @classmethod
    def from_dom(cls, news: Tag) -> 'News':
        """dom接受新版教务处网站`/tzgg.htm`页面中class="newlist1"的div标签"""
        return cls(
            raw_data={'dom': str(news)},
            id=news.get('href'), # type: ignore
            title=news.find('h3').text.strip(), # type: ignore
            publish_time=news.find('span').text.strip(), # type: ignore
            readcount=-1,
            publisher_name='null'
        )

    def __eq__(self, value) -> bool:
        return self.id == value.id

    def __hash__(self) -> int:
        return hash(self.id)


# ===== 接口定义 =====
class NewsGetter(ABC):
    """新闻获取器"""
    @abstractmethod
    def get_news(self) -> list[News]:
        """获取新闻列表"""


class GreetingGetter(ABC):
    """问候语获取器"""
    @abstractmethod
    def get(self) -> str:
        """获取问候语"""


# ===== 接口实现 =====
class JwzxNewsGetter(NewsGetter):
    """旧版教务在线新闻获取器"""
    def get_news(self) -> list[News]:
        """获取新闻列表"""
        newsjson = requests.get(NEWS_URL,headers={'User-Agent':UA}).json()
        # 检查是否为空
        if not newsjson['totalPage']:
            raise EmptyNewsError('获取新闻动态为空，请检查URL中mdq4jDUd字段是否正确！')
        # 新闻动态对象化
        return [News.from_json(i) for i in newsjson['data']]


class JwcNewsGetter(NewsGetter):
    """新版教务处新闻获取器"""
    options: FirefoxOptions

    def __init__(self):
        self.options = FirefoxOptions()
        self.options.add_argument('--headless')

    def __enter__(self):
        driver = Firefox(
            service=FirefoxService(FIREFOX_DRIVER_PATH),
            options=self.options
        )
        driver.delete_all_cookies()
        self._driver = driver
        return driver

    def get_news(self, driver: Firefox) -> list[News]:
        driver.get(NEWS_URL)
        time.sleep(5)
        dom = BeautifulSoup(driver.page_source, features='lxml')\
            .find('div', class_='newlist1')
        if not isinstance(dom, Tag):
            raise EmptyNewsError('新闻爬取失败')
        return [News.from_dom(news) for news in dom.find_all('a')[:20]]

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._driver.quit()


class RequestsAiGreetingGetter(GreetingGetter):
    """通过调用本地AI获取早安问候语"""
    def get(self) -> str:
        return requests.post(AI_URL, json={
            "stream": False,
            "model": "qwen2.5",
            "prompt": "请使用一句话向同学们问早安，50字左右"
        })\
            .json()\
            .get('response','早上好喵~愿这一天充满平安喜乐！')


# ===== 主业务逻辑 =====
class Bot:
    islazy:bool
    news_getter:NewsGetter
    greeting_getter:GreetingGetter

    def __init__(self,
                 islazy:bool,
                 news_getter:NewsGetter,
                 greeting_getter:GreetingGetter):
        self.islazy = islazy
        self.news_getter = news_getter
        self.greeting_getter = greeting_getter

        # 如果没有通知列表文件，则创建一个空的通知列表
        if not os.path.exists(NEWS_FILE):
            with open(NEWS_FILE,'w',encoding='utf-8') as f:
                f.write('[]')

    @property
    def news(self)->list[News]:
        '''获取当前的通知列表'''
        with open(NEWS_FILE,'r',encoding='utf-8') as f:
            news = json.load(f)
        # 将通知列表对象化
        return [News.from_dom(
            BeautifulSoup(i['dom'],features='lxml').find('a') # type: ignore
        ) for i in news]

    @news.setter
    def news(self,value:list[News]):
        '''设置当前的通知列表'''
        # 将当前通知列表保存到文件中
        with open(NEWS_FILE,'w',encoding='utf-8') as f:
            json.dump([i.raw_data for i in value],f,ensure_ascii=False,indent=2)

    def get_news(self)->list[News]:
        '''获取新闻动态'''
        assert isinstance(self.news_getter, JwcNewsGetter)
        with self.news_getter as driver:
            return self.news_getter.get_news(driver)

    def get_new_news(self)->list[News]:
        '''获取相较于上次获取新增的动态'''
        news = self.get_news()
        new_news = [i for i in news if i not in self.news]
        self.news = news
        return new_news

    def construct_post_text(self,news:list[News]):
        '''构造推文'''
        texts = []
        texts.append(time.strftime('今天是%m.%d'))
        texts.append(self.greeting_getter.get())
        if news:
            texts.append('最新教务通知：')
            for i,j in enumerate(news):
                texts.append(f'{i+1}. {j.title} ( https://jw.cqupt.edu.cn/{j.id} )')
        else:
            texts.append('教务在线没有新通知哦~')
        return '\n'.join(texts)

    def publish_new_news(self,msg:str):
        '''向订阅用户和群组推送推文'''
        for user in SUBSCRIBED_USERS:
            api_http.sendu(user,msg)
        for group in SUBSCRIBED_GROUPS:
            api_http.sendg(group,msg)


# ===== 异常定义 =====
class EmptyNewsError(ValueError):
    '''获取教务在线通知为空'''
    def __init__(self, t:str):
        self.t = t
    def __str__(self):
        return self.t


# ===== 主函数 =====
def main():
    bot = Bot(
        islazy='--lazy' in sys.argv,
        news_getter=JwcNewsGetter(),
        greeting_getter=RequestsAiGreetingGetter()
    )
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
