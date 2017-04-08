
import inspect
import time
import sys
import re
import traceback
import requests
import codecs
import bs4
class Config:
    HTML_HEADERS = {'Cookie': ''}
    SPIDE_UTIL = 201704060000
    HTTP_SLEEP_SEC = 400
    DEBUG = True

class Logger:
    """
    Implements a logger to sent log message to the log server.
    """
    def __init__(self, server='localhost', port=13333):
        pass
    @staticmethod
    def sent(self, msg):
        pass
    def _connect(self):
        pass
    @staticmethod
    def clean(self):
        pass

class User:
    def __init__(self):
        self.id = ''
        self.link = ''
        self.page_id = ''
        self.isCertified = 0
        self.level = 0
        self.followee = 0
        self.follower = 0
        self.number_of_tweets = 0
        self.label = ''
    def __str__(self):
        return  '%(id)s,%(link)s,%(page_id)s,%(isCertified)s,%(level)s,' \
                '%(followee)s,%(follower)s,%(number_of_tweets)s,%(label)s' % self.__dict__

class Weibo:
    def __init__(self):
        self.uid = ''
        self.mid = ''
        self.time = 0
        self.omid = ''
        self.content = ''
    def __str__(self):
        return '%(uid)s,%(mid)s,%(time)s,%(omid)s:%(content)s' % self.__dict__


def extractTextFromTag(tag):
    num_links = 0; num_videos = 0
    text = ''
    link = tag.attrs.get('href', None)
    is_user_link = tag.attrs.get('usercard', None)
    if link:
        title = tag.attrs.get('title', '')
        if is_user_link:
            text = tag.text.strip() + '[' + link + ']'
        else:
            if tag.find('i', 'ficon_cd_video'):
                num_videos = 1
                if title != '秒拍视频':
                    text = title
            elif tag.find('i', 'W_ficon'):
                num_links += 1
                if title != '网页链接':
                    text = title
        return (num_links, num_videos, text)
    for content in tag.contents:
        if isinstance(content, bs4.NavigableString):
            if content.strip() != '转发微博':
                text += content.strip()
        elif isinstance(content, bs4.Tag):
            links, videos, txt = extractTextFromTag(content)
            num_links += links
            num_videos += videos
            text += txt
        else:
            debug("%(content)s :: <%(type)s" % {'content': content, 'type': type(content)})
    return (num_links, num_videos, text)

def debug(msg):
    if Config.DEBUG:
        caller = inspect.stack()[1]
        prefix = caller.filename + ': ' + str(caller.lineno) + ' in <' + \
            caller.function + '> : '
        print(prefix + msg)


def loadSUB(fn):
    sub = ''
    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line == '':
                continue
            sub = line
    if sub == '':
        abort('.sub not found')
    Config.HTML_HEADERS['Cookie'] = sub
def sleepos(code):
    if code == 501:
        print("Too fast, going to sleep for " + str(Config.HTTP_SLEEP_SEC) + ' seconds')
        time.sleep(Config.HTTP_SLEEP_SEC)
        return True
    return False

def reliableGet(link):
    while True:
        try:
            print("Requesting: ", link)
            time.sleep(1)
            ret = requests.get(link, headers=Config.HTML_HEADERS)
            if sleepos(ret.status_code):
                continue
            return ret
        except requests.RequestException:
            traceback.print_exc()
def reliableHead(link):
    while True:
        try:
            print("Requesting header of: ", link)
            time.sleep(1)
            ret = requests.head(link, headers=Config.HTML_HEADERS)
            if sleepos(ret.status_code):
                continue
            return ret
        except requests.RequestException:
            traceback.print_exc()

def strip(script):
    script = re.sub(r'\\r', '', script)
    script = re.sub(r'\\n', '', script)
    script = re.sub(r'\\/', '/', script)
    script = re.sub(r'\\"', '"', script)
    return re.sub(r'\\t', '', script)
def extractHtmlFromScript(script):
    script = strip(script)
    if '<html>' in script or 'html' not in script:
        print('No html')
        return ''
    return script[script.find('div') - 1:-21]
def tsTonumber(ts):
    ts.strip()
    ts = re.sub('-', '', ts)
    ts = re.sub('\s+', '', ts)
    ts = re.sub(':', '', ts)
    return int(ts)
def abort(msg):
    Logger.clean()
    print(msg, "\tAbort")
    sys.exit(0)

def userLineSpliter(line):
    line = line.strip()
    if line == '':
        return None
    user = User()
    cols = line.split(',')
    user.id = cols[0]
    user.link = cols[1]
    user.page_id = cols[2]
    user.isCertified = int(cols[3])
    user.level = int(cols[4])
    user.followee = int(cols[5])
    user.follower = int(cols[6])
    user.number_of_tweets = int(cols[7])
    for label in cols[8:]:
        user.label += label
    return user

