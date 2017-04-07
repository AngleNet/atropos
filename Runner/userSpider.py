

import Spider.utils
import Spider.userSpider

if __name__ == '__main__':
    Spider.utils.loadSUB('.sub')
    Spider.userSpider.spideUsers('user_links')