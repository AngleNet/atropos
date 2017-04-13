
import Spider.utils
import requests
import re
if __name__ == '__main__':
    Spider.utils.loadSUB('../data/.sub')
    link = 'http://weibo.com/n/%E6%B4%B2%E5%B7%9DTerras-%E9%B8%AD%E5%98%B4%E5%85%BD?from=feed&loc=at'
    nick = link[link.find('n')+2:link.find('?')]
    link = 'http://weibo.com/aj/v6/user/newcard?ajwvr=6&name={nick}&type=1'.format(nick=nick)
    ret = requests.get(link, headers = Spider.utils.Config.HTML_HEADERS)
    text = ret.text
    text = re.sub(r'\\n', '', text)
    text = re.sub(r'\\r', '', text)
    text = re.sub(r'\\t', '', text)
    text  = text[5:-13]


