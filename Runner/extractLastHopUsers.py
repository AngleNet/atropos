import codecs
import sys
import glob
import os.path
sys.path.append('..')
import Spider.extractLastHopUsers

import Spider.utils
if __name__ == '__main__':
    data_dir = sys.argv[1]
    user_link_fname = 'user_links.original'
    with codecs.open(data_dir+user_link_fname, 'w', 'utf-8') as wd:
        crawled_uids = [os.path.basename(n).split('.')[0] for n in glob.glob(data_dir + '*.tweet')]
        for uid in crawled_uids:
            Spider.extractLastHopUsers.extractUser(uid, data_dir, wd)

    with codecs.open(user_link_fname + '.new', 'w', 'utf-8') as wd:
        Spider.extractLastHopUsers.cleanUserLinks(user_link_fname,
                                                  'user_links.new', data_dir, wd)