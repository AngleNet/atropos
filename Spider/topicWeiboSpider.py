
import Spider.utils
from bs4 import BeautifulSoup
import time, re, urllib.parse, traceback

class TRWeiboSpider:
    def __init__(self, topic):
        self.idx = topic.idx
        self.name = topic.name
        self.domain = self.idx[:6]
    def spide(self, nr_pages = 1):
        html  = self.spideFirstPage(1, 1)
        if html == '':
            return []
        contents = self.parseWeibo(html)
        since_id = self.retrieveSinceid(html)
        html = self.spideSecondPage(1, 1, since_id)
        if html == '':
            return contents
        contents.extend(self.parseWeibo(html))
        since_id = self.retrieveSinceid(html)
        html = self.spideThirdPage(2, 1, since_id)
        if html == '':
            return contents
        contents.extend(self.parseWeibo(html))
        since_id = self.retrieveSinceid(html)
        cp = 3
        for p in range(2, nr_pages+1):
            html = self.spideFirstPage(cp, p, since_id)
            if html == '':
                return contents
            contents.extend(self.parseWeibo(html))
            since_id= self.retrieveSinceid(html)
            if since_id == -1:
                break
            cp += 1
            html = self.spideSecondPage(cp, p, since_id)
            if  html == '':
                return contents
            contents.extend(self.parseWeibo(html))
            since_id = self.retrieveSinceid(html)
            if since_id == -1:
                break
            cp += 1
            html = self.spideThirdPage(cp, p, since_id)
            if html == '':
                return contents
            contents.extend(self.parseWeibo(html))
            since_id = self.retrieveSinceid(html)
            if since_id == -1:
                break
            cp += 1
        return contents

    def spideFirstPage(self, current_page, page, since_id = ''):
        link = " http://weibo.com/p/" + self.idx +  \
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
                timeout += 50
                continue
            break
        return html

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
        html = re.sub(r'\r', '', html)
        html = re.sub(r'\n', '', html)
        return html

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
        html = re.sub(r'\r', '', html)
        html = re.sub(r'\n', '', html)
        return html

    def retrieveSinceid(self, html):
        x = html.find('since_id')
        if x != -1:
            if html.find('last_since_id', x) == -1:
                return html[x+9:x+19]
            return urllib.parse.unquote(html[x+9:x+115])
        print("Never found Since_id")
        return ''

    def parseWeibo(self, html):
        """
        New parser.
        """
        box = BeautifulSoup(html, 'lxml')
        contents = []
        for wrap_box in box.find_all('div', 'WB_cardwrap'):
            try:
                if 'mid' not in wrap_box.attrs:
                    continue
                mid = wrap_box.attrs['mid']
                text = ''
                for text_box in wrap_box.find_all('div', 'WB_text'):
                    if 'list_con' in text_box.parent.attrs['class']:
                        continue
                    text += self.parseText(text_box, mid)
                contents.append(text)
            except:
                print("Error in parsing weibo: " + wrap_box.content)
                traceback.print_exc()
        return contents
    def parseText(self, text_box, mid):
        ltext = text_box.find('a', 'WB_text_opt')
        if ltext:
            print('Need to request long text')
            text_box = Spider.utils.reliableGetTweetHtml(mid)
            if text_box is None:
                Spider.utils.debug('Tweet %(mid)s is deleted' % dict(mid=mid))
                return ''
        num_urls, num_videos, text, found = Spider.utils.extractTextFromTag(text_box)
        text = re.sub(r'\\n', '', text)
        text = re.sub(r'\\r', '', text)
        text = re.sub(r'\u200b', '', text)
        text = re.sub(r'\xa0', '', text)
        if text == '转发微博':
            text = ''
        return text
if __name__ == '__main__':
    Spider.utils.loadSUB('.sub')
    topic = Spider.utils.Topic()
    topic.idx = '100808edc878c27b6da95848a3b9b278796885'
    topic.name = '#金钟仁邀您共赏andante#'
    spider = TRWeiboSpider(topic)
    spider.spide(4)