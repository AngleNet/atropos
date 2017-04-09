
import sys
sys.path.append('..')

import Spider.utils
import Spider.userSpider

if __name__ == '__main__':
    data_dir = sys.argv[1]
    Spider.utils.loadSUB(data_dir + '.sub')
    Spider.userSpider.spideUsers(data_dir + 'user_links')