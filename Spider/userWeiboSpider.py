
import Spider.utils
import traceback, codecs, re, datetime
import os.path
from bs4 import BeautifulSoup

class UserWeiboSpider:
    def __init__(self, user, latest, data_dir,spide_original=False):
        self.user = user
        self.latest = latest
        self.pids = ''
        self.latest = latest
        self.stop = False
        self.tweet_wd = codecs.open('{dir}/{uid}.tweet'.format(dir=data_dir, uid=user.id), 'a', 'utf-8')
        self.origin_tweet_wd  = codecs.open('{dir}/{uid}.origin_tweet'.format(dir=data_dir, uid=user.id), 'a', 'utf-8')
        self.spide_original = spide_original
    def start(self):
        if self.user.link == '' or self.user.id == '' or self.user.page_id == '':
            return
        page_num = 1
        while True:
            if page_num != 1:
                self.spidePage(page_num)
            else:
                self._spidePage()
            if self.stop:
                return
            self.spideSubPage(0, page_num)
            if self.stop:
                return
            self.spideSubPage(1, page_num)
            if self.stop:
                return
            page_num += 1
    def close(self):
        if self.tweet_wd:
            self.tweet_wd.close()
        if self.origin_tweet_wd:
            self.origin_tweet_wd.close()
    def spidePage(self, page_num):
        link = self.user.link + "?pids=" + self.pids + \
               "&is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1&" + \
                "page=" + str(page_num) + "&ajaxpagelet=1&ajaxpagelet_v6=1"
        ret = Spider.utils.reliableGet(link)
        feeds = Spider.utils.extractHtmlFromScript(ret.text)
        self.parseHtml(feeds)
    def _spidePage(self):
        ret = Spider.utils.reliableGet(self.user.link + '?profile_ftype=1&is_all=1')
        feeds = ''
        for script in BeautifulSoup(ret.text, 'lxml').find_all('script'):
            if'Pl_Official_MyProfileFeed__' in str(script):
                feeds = script
        feeds = str(feeds)
        x = feeds.find('Pl_')
        if x > 0:
            self.pids = feeds[x: x+29]
        else:
            self.stop = True
            return
        feeds = Spider.utils.extractHtmlFromScript(str(feeds))
        self.parseHtml(feeds)
    def spideSubPage(self, page_bar, page_num):
        link = "http://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6" + \
            "&domain=" + self.user.page_id[0:6] + "&profile_ftype=1&is_all=1"  + \
            "&pagebar=" + str(page_bar) + "&pl_name=" + self.pids + \
            "&id=" + self.user.page_id + "&feed_type=0&page=" + str(page_num) +\
            "&pre_page=" + str(page_num) + "&domain_op=" + self.user.page_id[0:6]
        ret =Spider.utils.reliableGet(link)
        feeds = ret.json()['data']
        feeds = Spider.utils.strip(feeds)
        self.parseHtml(feeds)
    def parseHtml(self, html):
        if html == '':
            self.stop = True
            return
        box = BeautifulSoup(html, 'lxml')
        turn_on = False
        for wrap_box in box.find_all('div', 'WB_cardwrap'):
            try:
                if 'mid' not in wrap_box.attrs or\
                        wrap_box.find('div', 'WB_cardtitle_b'):#Bypass mysterious box
                    continue
                mid = wrap_box.get('mid', None)
                isforward = wrap_box.attrs.get('isforward',  None)
                tweet_box = wrap_box.find('div', 'WB_detail')
                if tweet_box.find('a', ignore='ignore'):
                    continue
                turn_on = True
                #Spide expand box firstly.
                omid = 0
                omsg = None
                ouid = ''
                if isforward:
                    minfo = wrap_box.attrs['minfo'].split('&')
                    ouid = minfo[0].split('=')[-1]
                    omid = minfo[1].split('=')[-1]
                    omsg = self.parseTweetBox(tweet_box.find('div', 'WB_expand'),
                                             omid, True, 0)
                msg =  self.parseTweetBox(tweet_box, mid, False, omid)
                if self.stop:
                    break
                if msg:
                    self.tweet_wd.write(str(msg) + '\n')
                    if omsg:
                        omsg.uid = ouid
                        self.origin_tweet_wd.write(str(omsg) + '\n')
                    elif isforward:
                        self.origin_tweet_wd.write(str(omid) + '\n')
            except Exception:
                traceback.print_exc()
        if not turn_on:
            self.stop = True
    def parseTweetBox(self, box, mid, isforward, omid):
        if not box or not mid or box.find('div', 'WB_empty'):
            return None
        time_box = box.find('div', 'WB_from')
        mtime = Spider.utils.tsTonumber(time_box.a.attrs['title'])
        if not isforward and mtime <= self.latest:
            self.stop = True
            return None
        msg = Spider.utils.Weibo()
        msg.uid = self.user.id
        msg.mid = mid
        msg.omid = omid
        msg.time = mtime
        msg.content = self.parseText(box.find('div', 'WB_text'), mid)
        return msg

    def parseText(self, text_box, mid):
        num_urls = 0; num_videos = 0
        ltext = text_box.find('a', 'WB_text_opt')
        if ltext:
            print('Need to request long text')
            ret = Spider.utils.reliableGet('http://www.weibo.com/p/aj/mblog/getlongtext?ajwvr=6&mid=' \
                                    + mid)
            text_box = BeautifulSoup(ret.json()['data']['html'], 'lxml').body
        num_urls, num_videos, text, found= Spider.utils.extractTextFromTag(text_box, self.spide_original)
        text = re.sub(r'\\n', '', text)
        text = re.sub(r'\\r', '', text)
        text = re.sub(r'\u200b', '', text)
        text = re.sub(r'\xa0', '', text)
        if text == '转发微博':
            text = ''
        return '%(num_urls)s,%(num_videos)s,%(text)s' % dict(
            num_urls = num_urls,
            num_videos = num_videos,
            text = text,
        )

    def __str__(self):
        return self.user.link

def findLatestTimestamp(user, data_dir):
    """
    :param user: Type User
    :return:
    """
    fname = data_dir + user.id + '.tweet'
    if not os.path.exists(fname):
        return Spider.utils.Config.SPIDE_UTIL
    less = 0
    with codecs.open(fname, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line == '':
                continue
            cols = line[:line.find(':')].split(',')
            if less < int(cols[2]):
                less = int(cols[2])
    if less == 0:
        return Spider.utils.Config.SPIDE_UTIL
    return less

def spideUser(user, data_dir='',spide_original=False):
    """
    :param user:  Type User.
    :return:
    """
    latest = findLatestTimestamp(user, data_dir)
    spider = UserWeiboSpider(user, latest, data_dir, spide_original)
    try:
        spider.start()
    except Exception:
        traceback.print_exc()
    finally:
        spider.close()
if __name__ == '__main__':
    Spider.utils.loadSUB('../data/.sub')
    user = Spider.utils.User()
    user.link ='http://weibo.com/u/6130034198'
    user.page_id = '1005056130034198'
    user.id = '6130034198'
    latest = findLatestTimestamp(user, '')
    spider = UserWeiboSpider(user, latest)
    spider.start()
    spider.close()