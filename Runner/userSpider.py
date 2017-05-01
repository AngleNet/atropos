
import sys
sys.path.append('..')

import Spider.utils
import Spider.userSpider

if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    data_dir = proj_dir + '/data'
    Spider.utils.loadSUB(data_dir + '/.sub')
    users = Spider.utils.loadUsers(proj_dir + '/resource/user_links')
    Spider.userSpider.spideUsers(proj_dir, users)