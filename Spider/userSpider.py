
import Spider.utils
import codecs, traceback, re, requests, time
from bs4 import BeautifulSoup
"""
Need to change:
    sleep_seconds
"""
logger = Spider.utils.Logger()


def spideUser(link):
    if link == '':
        return None
    user = Spider.utils.User()
    user.link = link
    ret = Spider.utils.reliableGet(link)
    return parseHtml(ret.text, user)
def parseHtml(html, user):
    config = ''
    feeds = ''
    number_box = ''
    info_box = ''
    for script in BeautifulSoup(html, 'lxml').find_all('script'):
        if "$CONFIG['page_id']" in str(script):
            config = script
        elif 'Pl_Core_T8CustomTriColumn__' in str(script):
            number_box = script
        elif 'Pl_Core_UserInfo__' in str(script):
            info_box = script
    user.page_id, user.id = parseConfig(config)
    user.followee, user.follower, user.number_of_tweets = \
                    parseNumberBox(number_box)
    user.isCertified, user.level, user.label = parseUserInfo(info_box)
    return user
def parseConfig(script):
    if script == '':
        return (None, None)
    page_id = ''
    user_id = ''
    script = str(script.contents[0])
    for value in script.split(';'):
        if "['page_id']" in value:
            page_id = value.split("'")[-2]
        elif "['oid']" in value:
            user_id = value.split("'")[-2]
    if page_id == '' or user_id == '':
        print('Never Found')
    return (page_id, user_id)

def parseNumberBox(script):
    if script == '':
        return (0, 0, 0)
    followee = 0; follower = 0; number_of_tweets = 0
    script = Spider.utils.extractHtmlFromScript(str(script))
    script = BeautifulSoup(script, 'lxml')
    try:
        for box in script.find_all('td', class_='S_line1'):
            name = box.span.contents[0].strip()
            number = box.strong.contents[0].strip()
            if name == '关注':
                followee = int(number)
            elif name == '粉丝':
                follower = int(number)
            elif name == '微博':
                number_of_tweets = int(number)
        return (followee, follower, number_of_tweets)
    except Exception:
        traceback.print_exc()

def parseUserInfo(script):
    if script == '':
        return (0, 0, '')
    isCertified = 0; level = 0; label = ''
    script = Spider.utils.extractHtmlFromScript(str(script))
    script = BeautifulSoup(script, 'lxml')
    try:
        certified_box = script.find('p', class_='verify')
        if certified_box:
            isCertified = 1
            level = certified_box.find('span', class_='S_line1').span.contents[0].split('.')[-1]
        for box in script.find_all('li', class_='S_line2'):
            item = box.find('span', class_='item_text')
            if 'Lv' in str(item):
                level = int(item.span.contents[0].strip().split('.')[-1])
            elif '标签' in str(item):
                for label_box in item.find_all('a'):
                    label += label_box.contents[0] + ';'
        return (isCertified, level, label)
    except Exception:
        traceback.print_exc()

def spideUsers(proj_dir):
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'
    users = dict()
    with codecs.open(data_dir + '/user_links', 'r','utf-8') as f:
        for line in f.readlines():
            user = Spider.utils.userLineSpliter(line)
            if user and user.id not in  users:
                users[user.id] = user
    with codecs.open(res_dir + 'user_links.new', 'w', 'utf-8') as f:
        for user in users.values():
            try:
                user = spideUser(user.link)
                if user is not None:
                    f.write(str(user) + '\n')
            except Exception:
                pass
if __name__ == '__main__':
    #Spider.utils.loadSUB('sub.sub')
    spideUsers('user_links')
