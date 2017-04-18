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
        proj_dir = '../'
    else:
        proj_dir = sys.argv[1]
    res_dir = proj_dir + 'result/'
    data_dir = proj_dir + 'data/'
    Spider.utils.loadSUB(data_dir+'.sub')
    ouser_link_fname = 'user_links.original.new'
    user_links = Spider.utils.loadOriginalUserLinks(data_dir+ ouser_link_fname)
    for user_link in user_links.values():
        user = Spider.utils.userLinkToUser(user_link)
        if user.id == '' or user.link == '' or user.page_id == '':
            Spider.utils.debug('required fields are empty in {user}'.format(user=str(user)))
            continue
        Spider.userWeiboSpider.spideUser(user, data_dir)
