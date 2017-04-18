import codecs
import sys
import time
import requests
import traceback
sys.path.append('..')
import Spider.utils
import Spider.userSpider

if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '../'
    else:
        proj_dir = sys.argv[1]
    res_dir = proj_dir + 'result/'
    data_dir = proj_dir + 'data/'
    Spider.utils.loadSUB(data_dir+'.sub')
    ouser_link_fname = 'user_links.original.no_pid'
    user_links = Spider.utils.loadOriginalUserLinks(data_dir+ ouser_link_fname)
    with codecs.open(res_dir + 'user_links.original.new', 'w', 'utf-8') as fd:
        for user_link in user_links.values():
            if 'http' not in user_link.link:
                user_link.link = 'http://weibo.com/u/{uid}'.format(uid=user_link.ouid)
                while True:
                    try:
                        print('Requesting head of ' + user_link.link)
                        time.sleep(1)
                        ret = requests.head(user_link.link,
                                            headers=Spider.utils.Config.HTML_HEADERS,
                                            allow_redirects=False)
                        if Spider.utils.sleepos(ret.status_code):
                            continue
                        if ret.status_code == 302:
                            if ret.headers['location'].find('?') == -1:
                                user_link.link = 'http://weibo.com' + ret.headers['location']
                            else:
                                user_link.link = ret.headers['location'].split('?')[0]
                        break
                    except Exception:
                        traceback.print_exc()
            user = Spider.userSpider.spideUser(user_link.link)
            fd.write(str(user) + '\n')