import codecs
import sys
sys.path.append('..')
import Spider.userWeiboSpider

import Spider.utils
if __name__ == '__main__':
    data_dir = sys.argv[1]
    Spider.utils.loadSUB(data_dir+'.sub')
    with codecs.open('user_links.new', 'r', 'utf-8') as fd:
        for line in fd.readlines():
            user = Spider.utils.userLineSpliter(line)
            if user:
                Spider.userWeiboSpider.spideUser(user, data_dir)


