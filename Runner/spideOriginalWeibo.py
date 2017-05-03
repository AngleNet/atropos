import codecs
import sys
import time
import requests
import traceback
sys.path.append('..')
import Spider.utils
import Spider.userWeiboSpider


if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'
    Spider.utils.loadSUB(data_dir + '/.sub')
    with codecs.open(data_dir + '/user_links.new', 'r', 'utf-8') as fd:
        for line in fd.readlines():
            user = Spider.utils.userLineSpliter(line)
            if user.id == '' or user.link == '' or user.page_id == '':
                Spider.utils.debug('required fields are empty in {user}'.format(user=str(user)))
                continue
            Spider.userWeiboSpider.spideUser(user, res_dir, spide_original=True)

