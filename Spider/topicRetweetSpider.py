import sys, traceback, os.path, time, urllib.parse
import re
from bs4 import BeautifulSoup
import codecs, json
sys.path.append('..')
import Spider.utils

class TRWeiboSpider:
    def __init__(self, topic, ):
        self.idx = topic.idx
        self.name = topic.name
        self.domain = self.idx[:6]
    def spide(self, nr_pages = 1):
        html  = self.spideFirstPage(1, 1)
        if html == '':
            return dict()
        contents = self.parseWeibo(html)
        since_id = self.retrieveSinceid(html)
        html = self.spideSecondPage(1, 1, since_id)
        if html == '':
            return contents
        Spider.utils.dictExtend(contents, self.parseWeibo(html))
        since_id = self.retrieveSinceid(html)
        html = self.spideThirdPage(2, 1, since_id)
        if html == '':
            return contents
        Spider.utils.dictExtend(contents, self.parseWeibo(html))
        since_id = self.retrieveSinceid(html)
        cp = 3
        for p in range(2, nr_pages+1):
            html = self.spideFirstPage(cp, p, since_id)
            if html == '':
                return contents
            Spider.utils.dictExtend(contents, self.parseWeibo(html))
            since_id= self.retrieveSinceid(html)
            if since_id == -1:
                break
            cp += 1
            html = self.spideSecondPage(cp, p, since_id)
            if  html == '':
                return contents
            Spider.utils.dictExtend(contents, self.parseWeibo(html))
            since_id = self.retrieveSinceid(html)
            if since_id == -1:
                break
            cp += 1
            html = self.spideThirdPage(cp, p, since_id)
            if html == '':
                return contents
            Spider.utils.dictExtend(contents, self.parseWeibo(html))
            since_id = self.retrieveSinceid(html)
            if since_id == -1:
                break
            cp += 1
        return contents

    def spideFirstPage(self, current_page, page, since_id = ''):
        link = "http://weibo.com/p/" + self.idx +  \
                    "?pids=Pl_Third_App__11&current_page=" + str(current_page) + "&page=" + \
                    str(page) + "&ajaxpagelet=1&ajaxpagelet_v6=1"
        if since_id == '' and current_page != 1:
            return ''
        if since_id  != '':
            link += "&since_id=" + since_id
        timeout = 10
        while True:
            ret = Spider.utils.reliableGet(link)
            html = Spider.utils.extractHtmlFromScript(ret.text)
            if html == '':
                time.sleep(timeout)
                continue
            break
        return Spider.utils.strip(html)

    def spideSecondPage(self, current_page, page, since_id):
        if since_id == '':
            return ''
        link = "http://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100808&mod=TAB"\
                    "&pagebar=0&tab=home&current_page=" + str(current_page) + \
                    "&pl_name=Pl_Third_App__11&id=" + str(self.idx) + \
                    "&feed_type=1&page=" + str(page) + "&pre_page=" + str(page) +\
                    "&domain_op=100808&since_id=" + str(since_id)
        ret = Spider.utils.reliableGet(link)
        html = ret.json()['data']
        return Spider.utils.strip(html)

    def spideThirdPage(self, current_page, page, since_id):
        if since_id == '':
            return ''
        link = "http://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100808&mod=TAB" \
               "&pagebar=1&tab=home&current_page=" + str(current_page) + \
               "&pl_name=Pl_Third_App__11&id=" + str(self.idx) + \
               "&feed_type=1&page=" + str(page) + "&pre_page=" + str(page) + \
               "&domain_op=100808&since_id=" + str(since_id)
        ret = Spider.utils.reliableGet(link)
        html = ret.json()['data']
        return Spider.utils.strip(html)

    def retrieveSinceid(self, html):
        x = html.find('since_id')
        if x != -1:
            if html.find('last_since_id', x) == -1:
                return html[x+9:x+19]
            return urllib.parse.unquote(html[x+9:x+115])
        print("Never found Since_id")
        return ''

    def parseWeibo(self, html):
        tweets = dict()
        if html == '':
            return tweets
        box = BeautifulSoup(html, 'lxml')
        for wrap_box in box.find_all('div', 'WB_cardwrap'):
            try:
                if 'mid' not in wrap_box.attrs:#Bypass mysterious box
                    continue
                mid = wrap_box.get('mid', None)
                uid = wrap_box.get('tbinfo', None)
                if uid and uid.split('=')[0].strip() == 'ouid':
                    uid = uid.split('=')[1].strip()
                else:
                    Spider.utils.debug(uid)
                if wrap_box.attrs.get('isforward',  None):
                    #Spider.utils.debug('Find a retweet: {text}'.format(text=wrap_box.prettify()))
                    continue
                tweet_box = wrap_box.find('div', 'WB_detail')
                if tweet_box.find('a', ignore='ignore'):
                    continue
                #Spide expand box firstly.
                msg =  self.parseTweetBox(tweet_box, mid, uid)
                if msg and mid not in tweets:
                    tweets[mid] = msg
            except Exception:
                traceback.print_exc()
        return tweets
    def parseTweetBox(self, box, mid, uid):
        if not box or not mid or box.find('div', 'WB_empty'):
            return None
        time_box = box.find('div', 'WB_from')
        mtime = Spider.utils.tsTonumber(time_box.a.attrs['title'])
        if mtime <= Spider.utils.Config.SPIDE_UTIL:
            return None
        msg = Spider.utils.Weibo()
        msg.uid = uid
        msg.mid = mid
        msg.omid = ''
        msg.time = mtime
        msg.content = self.parseText(box.find('div', 'WB_text'), mid)
        return msg

    def parseText(self, text_box, mid):
        ltext = text_box.find('a', 'WB_text_opt')
        if ltext:
            print('Need to request long text')
            ret = Spider.utils.reliableGet('http://www.weibo.com/p/aj/mblog/getlongtext?ajwvr=6&mid=' \
                                    + mid)
            text_box = BeautifulSoup(ret.json()['data']['html'], 'lxml').body
        num_urls, num_videos, text, found = Spider.utils.extractTextFromTag(text_box, spide_original=False, found=False)
        text = Spider.utils.strip(text)
        text = re.sub(r'\u200b', '', text)
        text = re.sub(r'\xa0', '', text)
        if text == '转发微博':
            text = ''
        return '%(num_urls)s,%(num_videos)s,%(text)s' % dict(
            num_urls = num_urls,
            num_videos = num_videos,
            text = text,
        )
def extractRetweets(html, tweet):
    retweets = dict()
    if html == '':
        return retweets
    box = BeautifulSoup(html, 'lxml')
    if box.find('div', 'WB_empty'):
        return retweets
    for wrap_box in box.find_all('div', 'list_li'):
        if 'mid' not in wrap_box.attrs:
            continue
        msg = Spider.utils.Weibo()
        msg.mid = wrap_box.attrs['mid']
        if msg.mid in retweets:
            continue
        text_box = wrap_box.find('div', 'WB_text')
        msg.uid = text_box.find('a', attrs={'node-type': 'name'}).attrs['usercard'].split('=')[1]
        from_box = wrap_box.find('div', 'WB_from')
        msg.time = Spider.utils.tsTonumber(from_box.find('a', attrs={'node-type': 'feed_list_item_date'}).attrs['title'])
        msg.omid = tweet.mid
        msg.content = parseText(text_box.find('span', attrs={'node-type': 'text'}), msg.mid)
        retweets[msg.mid] = msg
    return retweets

def parseText(text_box, mid):
    ltext = text_box.find('a', 'WB_text_opt')
    if ltext:
        print('Need to request long text')
        ret = Spider.utils.reliableGet('http://www.weibo.com/p/aj/mblog/getlongtext?ajwvr=6&mid=' \
                                       + mid)
        text_box = BeautifulSoup(ret.json()['data']['html'], 'lxml').body
    num_urls, num_videos, text, found = Spider.utils.extractTextFromTag(text_box, spide_original=False, found=False)
    text = Spider.utils.strip(text)
    text = re.sub(r'\u200b', '', text)
    text = re.sub(r'\xa0', '', text)
    if text == '转发微博':
        text = ''
    return '%(num_urls)s,%(num_videos)s,%(text)s' % dict(
        num_urls=num_urls,
        num_videos=num_videos,
        text=text,
    )

def spideRetweets(tweet, pages=1):
    retweets = dict()
    if tweet.mid == '':
        return retweets
    link ='http://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id={mid}&page=1'.format(
        mid = tweet.mid)
    ret = Spider.utils.reliableGet(link)
    ret_json = json.loads(ret.text)
    if not ret_json.get('data') or \
        ret_json['data'].get('html') is None or ret_json['data'].get('page') is None:
        return retweets
    total_pages = int(ret_json['data']['page']['totalpage'])
    if total_pages < pages:
        pages = total_pages
    Spider.utils.dictExtend(retweets, extractRetweets(
        Spider.utils.strip(ret_json['data']['html']), tweet))
    for page in range(2, pages+1):
        link = link[:-1] + str(page)
        ret = Spider.utils.reliableGet(link)
        ret_json = json.loads(ret.text)
        if not ret_json.get('data') or \
                        ret_json['data'].get('html') is None or ret_json['data'].get('page'):
            continue
        Spider.utils.dictExtend(retweets, extractRetweets(
            Spider.utils.strip(ret_json['data']['html']), tweet))
    return retweets

if __name__ == '__main__':
    if len(sys.argv) == 1:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    data_dir = proj_dir + '/data'
    result_dir = proj_dir + '/result'

    Spider.utils.loadSUB(data_dir+'/.sub')
    topics = dict()
    with codecs.open(data_dir+'/trending_topics', 'r', 'utf-8') as fd:
        for line in fd.readlines():
            topic = Spider.utils.topicLineSpliter(line)
            if topic and topic.idx not in topics:
                topics[topic.idx] = topic
    #Spide topic related tweets
    for topic in topics.values():
        if os.path.exists('{dir}/{idx}.origin_tweet'.format(dir=result_dir, idx=topic.idx)):
            Spider.utils.debug('Bypass topic {idx}'.format(idx=topic.idx))
            continue
        spider = TRWeiboSpider(topic)
        tweets = spider.spide(nr_pages=3)
        with codecs.open('{dir}/{idx}.origin_tweet'.format(dir=result_dir, idx=topic.idx), 'w', 'utf-8') as fd:
            for tweet in tweets.values():
                fd.write(str(tweet) + '\n')
        with codecs.open('{dir}/{idx}.tweet'.format(dir=result_dir, idx=topic.idx), 'w', 'utf-8') as fd:
            for tweet in tweets.values():
                retweets = spideRetweets(tweet, pages=2)
                for retweet in retweets.values():
                    fd.write(str(retweet) + '\n')