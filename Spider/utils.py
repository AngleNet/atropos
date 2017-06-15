
import inspect
import time
import sys
import re
import traceback
import requests
import codecs
import bs4
import os.path
import json

class Config:
    HTML_HEADERS = {'Cookie': ''}
    SPIDE_UTIL = 201706150000
    SAMPLE_WINDOW_START = 201706150000
    SAMPLE_WINDOW_END = 201706152359
    HTTP_SLEEP_SEC = 400
    DEBUG = True
    USER_LINKS= dict()
class Logger:
    """
    Implements a logger to sent log message to the log server.
    """
    def __init__(self, server='localhost', port=13333):
        pass
    @staticmethod
    def sent(msg):
        pass
    def _connect(self):
        pass
    @staticmethod
    def clean():
        pass

class OriginalUserLink:
    def __init__(self):
        self.ouid = ''
        self.link = ''
        self.pid = ''
        self.time = ''
        self.omid = list()
    def __str__(self):
        rstr = '{ouid},{link},pid:{pid},time:{time}'.format(ouid=self.ouid, link=self.link,
                                                            pid=self.pid, time=self.time)
        for i in self.omid:
            rstr += ',omid:{omid}'.format(omid=i)
        return rstr

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

class Topic:
    def __init__(self):
        self.idx = ''
        self.reads = 0
        self.name = ''
        self.trindex = 0
    def __str__(self):
        return ('%(idx)s,%(reads)s,%(name)s, %(trindex)s' % self.__dict__)

class Weibo:
    def __init__(self):
        self.uid = ''
        self.mid = ''
        self.time = 0
        self.omid = ''
        self.content = ''
    def getContentLastHop(self):
        """
        Return the last hop user id if this weibo contains is retweeted, otherwise
        None.
        :return:
        """
        if self.content == '':
            return None
        texts = self.content.split(',')[2:]
        txt = ''
        for t in texts:
            txt += t.strip() + ','
        if txt != '':
            txt = txt[:-1]
        hops = self._findOnpathRetweetUser(txt)
        if hops:
            if len(hops[0].split(',')) != 2:
                return None
            return hops[0]
        return None
    def seperateContent(self):
        num_links = 0; num_videos = 0;  pure_text = ''
        if self.content == '' or len(self.content.split(',')) < 3:
            debug('Malformed content:  {content}'.format(content=self.content))
            return (num_links, num_videos, pure_text)
        cols = self.content.split(',')
        num_links = int(cols[0])
        num_videos = int(cols[1])
        text = ''
        for col in cols[2:]:
            text += col
        pure_text = Weibo.getPureText(text)
        return (num_links,num_videos, pure_text)
    @staticmethod
    def getPureText(text):
        rem = text
        text = ''
        while len(rem) > 0:
            s = rem.find('[')
            ss = rem.find('@')
            t = rem.find(']')
            if s != -1 and ss != -1 and ss < s and t > s:
                text += rem[:s]
                rem = rem[t + 1:]
            elif t > s:
                text += rem[:s]
                rem = rem[t + 1:]
            elif t >= 0:
                text += rem[:t]
                rem = rem[t + 1:]
            else:
                text += rem
                rem = ''
        text = re.sub('秒拍', '', text)
        text = re.sub('视频', '', text)
        return text
    def _findOnpathUser(self, txt):
        pass
    def _findOnpathRetweetUser(self, txt):
        if txt == '':
            return None
        s = txt.find('//@')
        if s == -1:
            return None
        ss = txt[s + 3:].find('[')
        if ss == -1:
            debug('Missing [ after nick name')
            debug(txt)
            return None
        st = txt[s + 3 + ss + 1:].find(']')
        if st == -1:
            debug('Missing ] after nick name')
            debug(txt)
            return None
        links = list()
        links.append(txt[s + 3 + ss+1: s + 3 + ss + 1 + st])
        txt = txt[s + 3 + ss + 1 + st + 1:]
        next_links = self._findOnpathRetweetUser(txt)
        if next_links:
            links.extend(next_links)
        return links
    def __str__(self):
        return '%(uid)s,%(mid)s,%(time)s,%(omid)s:%(content)s' % self.__dict__

class WeiboSample:
    def __init__(self):
        self.id = ''
        self.omid = ''
        self.uid = ''
        self.time = ''
        self.ouid = ''
        self.otime = ''
        self.truly_retweeted = 0
        self.num_links = 0
        self.num_videos = 0
        self.text = ''
    def __str__(self):
        return '%(id)s,%(omid)s,%(uid)s,%(time)s,%(ouid)s,%(otime)s,' \
               '%(truly_retweeted)s,%(num_links)s,%(num_videos)s,%(text)s' % self.__dict__


class Sample:
    def __init__(self):
        self.id = ''
        self.uid = ''
        self.time = ''
        self.ouid = ''
        self.otime= ''
        self.truly_retweeted = 0
        self.num_links = 0
        self.num_videos = 0
        self.trindex = 0
    def loadFromWeibo(self,weibo):
        if weibo is None:
            return
        self.id = weibo.id
        self.uid = weibo.uid
        self.time = weibo.time
        self.ouid = weibo.ouid
        self.otime = weibo.otime
        self.truly_retweeted = weibo.truly_retweeted
        self.num_links = weibo.num_links
        self.num_videos = weibo.num_videos
    def __str__(self):
        return '%(id)s,%(uid)s,%(time)s,%(ouid)s,%(otime)s,%(truly_retweeted)s,' \
               '%(num_links)s,%(num_videos)s,%(trindex)s' % self.__dict__

class TrainningSample:
    def __init__(self):
        self.id = ''
        self.certified = 0
        self.num_followers = 0
        self.num_urls = 0
        self.num_videos = 0
        self.content_len = 0
        self.similarity = 0
        self.retweet_rate = 0
        self.interact_rate = 0
        self.trending_index = 0
        self.pos = 0

    def __str__(self):
        return '%(id)s,%(certified)s,%(num_followers)s,%(num_urls)s,' \
               '%(num_videos)s,%(content_len)s,%(similarity)s,%(retweet_rate)s,' \
               '%(interact_rate)s,%(trending_index)s,%(pos)s' % self.__dict__

    @staticmethod
    def lineSpliter(line):
        line = line.strip()
        if line == '':
            return None
        samp = TrainningSample()
        cols = line.split(',')
        samp.id = cols[0]
        samp.certified = int(cols[1])
        samp.num_followers = int(cols[2])
        samp.num_urls = int(cols[3])
        samp.num_videos = int(cols[4])
        samp.content_len =  int(cols[5])
        samp.similarity = float(cols[6])
        samp.retweet_rate = float(cols[7])
        samp.interact_rate = float(cols[8])
        samp.trending_index = float(cols[9])
        samp.pos = int(cols[10])
        return samp


def sampleLineSpliter(line):
    line = line.strip()
    if line == '':
        return None
    samp = Sample()
    cols = line.split(',')
    samp.id = cols[0]
    samp.uid = cols[1]
    samp.time = cols[2]
    samp.ouid = cols[3]
    samp.otime = cols[4]
    samp.truly_retweeted = cols[5]
    samp.num_links = cols[6]
    samp.num_videos = cols[7]
    samp.trindex = cols[8]
    return samp

def uidToLink(uid):
    if uid.strip() == '':
        return ''
    link = 'http://weibo.com/u/{uid}'.format(uid=uid)
    tries = 0
    while True:
        try:
            tries += 1
            if tries > 4:
                return ''
            ret = requests.head(link, headers=Config.HTML_HEADERS, allow_redirects=False)
            if sleepos(ret.status_code):
                continue
            elif ret.status_code >= 300 and ret.status_code < 400 \
                    and ret.headers.get('location', None):
                return 'http://weibo.com' + ret.headers['location']
            else:
                return link
        except Exception:
            traceback.print_exc()
def nickLinkTouid(link):
    link = link.strip()
    if link in Config.USER_LINKS:
        return Config.USER_LINKS[link]
    ret_link = ''
    tries = 0
    while True:
        try:
            tries += 1
            if tries > 4:
                return 'NULL'
            ret = requests.head(link, headers=Config.HTML_HEADERS, allow_redirects=False)
            if sleepos(ret.status_code):
                continue
            elif ret.status_code >= 300 and ret.status_code < 400 \
                    and ret.headers.get('location', None) and ret.headers['location'].find('?') != -1:
                ret_link =  ret.headers['location'][:ret.headers['location'].find('?')]
                break
        except Exception:
            traceback.print_exc()
    nick = link[link.find('n')+2:link.find('?')]
    ret = reliableGet( 'http://weibo.com/aj/v6/user/newcard?ajwvr=6&name={nick}&type=1'.format(nick=nick), sleep=False)
    ret_json = json.loads(ret.text.strip()[5:-13])
    uid = ''
    if ret_json['msg'] == 'ok':
        box = bs4.BeautifulSoup(strip(ret_json['data']), 'lxml')
        for tag in box.find_all('a'):
            if tag.attrs.get('uid', None):
                uid = tag.attrs['uid']
                break
    Config.USER_LINKS[link] = (uid, ret_link)
    return (uid, ret_link)

def extractTextFromTag(tag, spide_original=False, found=False, last_tag_text=''):
    last_tag_text = last_tag_text.strip()
    num_links = 0; num_videos = 0
    text = ''
    link = tag.attrs.get('href', None)
    is_user_link = tag.attrs.get('usercard', None)
    if link:
        title = tag.attrs.get('title', '')
        if is_user_link:
            text = tag.text.strip()
            if not spide_original and last_tag_text[-2:] == '//' and not found:
                try:
                    uid, link = nickLinkTouid(link)
                except Exception:
                    uid, link = ('', '')
                text = '{text}[{uid},{link}]'.format(text=text, uid=uid, link=link)
                found = True
            else:
                text = '{text}[{uid},{link}]'.format(text=text, uid='', link='')
        else:
            if tag.find('i', 'ficon_cd_video'):
                num_videos = 1
                if title.find('秒拍视频') != -1:
                    text = title
            elif tag.find('i', 'W_ficon'):
                num_links += 1
                if title != '网页链接':
                    text = title
            else:
                text = tag.text.strip()
                if len(text) > 0 and text[0] == '#':
                    #Trending Topic
                    link = topicNameToIndex(link)
                    text = '%(text)s[%(link)s]' % dict(text=text, link=link)
                else:
                    num_links += 1
        return (num_links, num_videos, text, found)
    for content in tag.contents:
        if isinstance(content, bs4.NavigableString):
            if content.strip() != '转发微博':
                text += content.strip()
        elif isinstance(content, bs4.Tag):
            links, videos, txt, found = extractTextFromTag(content, spide_original, found, text)
            num_links += links
            num_videos += videos
            text += txt
        else:
            debug("%(content)s :: <%(type)s" % {'content': content, 'type': type(content)})
    return (num_links, num_videos, text, found)
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
def topicNameToIndex(link):
    tries = 0
    while True:
        try:
            tries += 1
            if tries > 4:
                return 'NULL'
            ret = requests.get(link, headers=Config.HTML_HEADERS, allow_redirects=False)
            if sleepos(ret.status_code):
                continue
            elif ret.status_code >= 300 and ret.status_code < 400\
                    and ret.headers.get('location', None) and ret.headers['location'].find('?') != -1:
                return ret.headers['location'][:ret.headers['location'].find('?')]
        except Exception:
            traceback.print_exc()

def reliableGet(link, sleep=True):
    link = link.strip()
    while True:
        try:
            print("Requesting: ", link)
            if sleep:
                time.sleep(1)
            ret = requests.get(link, headers=Config.HTML_HEADERS)
            if sleepos(ret.status_code):
                continue
            return ret
        except requests.RequestException:
            traceback.print_exc()
def reliableHead(link):
    link = link.strip()
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
def reliableGetTweetHtml(mid):
    mid = str(mid)
    timeout = 0
    while True:
        try:
            timeout += 5
            if timeout > 20:
                return None
            ret = reliableGet('http://www.weibo.com/p/aj/mblog/getlongtext?ajwvr=6&mid=' \
                                    + mid)
            text_box = bs4.BeautifulSoup(ret.json()['data']['html'], 'lxml').body
            return text_box
        except Exception:
            debug("Error while retreiving tweet " + mid)
            debug(traceback.format_exc())
            time.sleep(timeout)

def strip(script):
    script = re.sub(r'\\r', '', script)
    script = re.sub(r'\\n', '', script)
    script = re.sub(r'\\/', '/', script)
    script = re.sub(r'\\"', '"', script)
    script = re.sub(r'\r', '',script)
    script = re.sub('&nbsp;', '', script)
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
    if len(cols) < 9:
        debug('wrong line for user: {line}'.format(line=line))
        return None
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

def tweetLineSpliter(line):
    line = line.strip()
    if line == '':
        return None
    weibo = Weibo()
    loc = line.find(':')
    cols = line[:loc].split(',')
    if not re.match(r'[0-9]+', cols[0]) or re.match(r'[0-9]+', cols[0]).group() != cols[0]\
            or len(cols) < 4:
        debug(line)
        return None
    weibo.uid = cols[0]
    weibo.mid = cols[1]
    weibo.time  = cols[2]
    weibo.omid = cols[3]
    weibo.content = line[loc+1:]
    return weibo

def originalUserLinkSpiliter(line):
    line = line.strip()
    if line == '':
        return None
    link = OriginalUserLink()
    cols = line.split(',')
    link.ouid = cols[0]
    link.link = cols[1]
    for col in cols[2:]:
        pair = col.split(':')
        if pair[0] == 'time':
            link.time = pair[1]
        elif pair[0] == 'pid':
            link.pid = pair[1]
        elif pair[0] == 'omid':
            if pair[1] not in link.omid:
                link.omid.append(pair[1])
        else:
            debug('mysterious key word {key} in line {line}'.format(key=pair[0], line=line))
    return link

def weiboSampleLineSpliter(line):
    line = line.strip()
    if line == '':
        return None
    samp = WeiboSample()
    cols = line.split(',')
    samp.id = cols[0]
    samp.omid = cols[1]
    samp.uid = cols[2]
    samp.time = cols[3]
    samp.ouid = cols[4]
    samp.otime = cols[5]
    samp.truly_retweeted = cols[6]
    samp.num_links = cols[7]
    samp.num_videos = cols[8]
    for text in cols[9:]:
        samp.text += text + ','
    if len(samp.text) > 0:
        samp.text = samp.text[:-1]
    return samp

def loadUsers(fname):
    if not os.path.exists(fname):
        debug('{fname} does not exists.'.format(fname=fname))
        return None
    users = dict()
    with codecs.open(fname, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            user = userLineSpliter(line)
            if user and user.id not in users:
                users[user.id] = user
    return users
def loadOriginalUserLinks(fname):
    """
    This function will remove all duplicate lines with same uid
    :param fname:
    :return:
    """
    if not os.path.exists(fname):
        debug('{fname} does not exists.'.format(fname=fname))
        return None
    links = dict()
    with codecs.open(fname, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            link = originalUserLinkSpiliter(line)
            if link and link.ouid not in links:
                links[link.ouid] = link
    return links

def loadTweets(fname, use_filter=True):
    def timeFilter(tweet):
        return int(tweet.time) >= Config.SAMPLE_WINDOW_START and \
                int(tweet.time) <= Config.SAMPLE_WINDOW_END
    if not os.path.exists(fname):
        debug('{fname} does not exists.'.format(fname=fname))
        return None
    if os.path.basename(fname).split('.')[-1] == 'origin_tweet' or not use_filter:
        filter = lambda tweet: True
    else:
        filter = timeFilter
    tweets = dict()
    with codecs.open(fname, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            tweet = tweetLineSpliter(line)
            if tweet and tweet.mid not in tweets \
                and filter(tweet):
                tweets[tweet.mid] = tweet
    return tweets

def loadTrendingTopics(fname):
    if not os.path.exists(fname):
        debug('{fname} does not exists.'.format(fname=fname))
        return None
    topics = dict()
    with codecs.open(fname, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            topic = topicLineSpliter(line)
            if topic and topic.idx not in topics:
                topics[topic.idx] = topic
    return topics

def getTweets(uid, user_tweets, path):
    if uid in user_tweets:
        return user_tweets[uid]
    user_tweets[uid] = loadTweets(path)
    return user_tweets[uid]
def topicLineSpliter(line):
    line = line.strip()
    cols = line.split(',')
    if len(cols) < 3:
        return None
    topic = Topic()
    topic.idx = cols[0]
    topic.reads = int(cols[1])
    for _ in cols[2:]:
        topic.name += _ + ','
    topic.name = topic.name[:-1]
    return topic
def writeList(fname, items):
    if items is None:
        return
    with codecs.open(fname, 'w', 'utf-8') as fd:
        for item in items:
            fd.write(str(item) + '\n')

def userLinkToUser(user_link):
    user = User()
    user.id = user_link.ouid
    user.link = user_link.link
    user.page_id = user_link.pid
    return user

def dictExtend(d1, d2):
    for v in d2.keys():
        if v not in d1:
            d1[v] = d2[v]

