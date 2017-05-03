import codecs
import sys
sys.path.append('..')
import Spider.userWeiboSpider

import Spider.utils
if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'
    Spider.utils.loadSUB(data_dir+'/.sub')
    with codecs.open(data_dir + '/user_links.new', 'r', 'utf-8') as fd:
        for line in fd.readlines():
            user = Spider.utils.userLineSpliter(line)
            if user:
                Spider.userWeiboSpider.spideUser(user, res_dir)


