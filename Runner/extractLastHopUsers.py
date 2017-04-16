import codecs
import sys
import glob
import os.path
sys.path.append('..')
import Spider.extractLastHopUsers

import Spider.utils
if __name__ == '__main__':
    proj_dir = sys.argv[1]
    data_dir = proj_dir+'data/'
    result_dir = proj_dir + 'result/'
    user_link_fname = 'user_links.original'
    with codecs.open(result_dir+user_link_fname, 'w', 'utf-8') as wd:
        crawled_uids = [os.path.basename(n).split('.')[0] for n in glob.glob(data_dir + '*.tweet')]
        for uid in crawled_uids:
            Spider.extractLastHopUsers.extractUser(uid, data_dir, wd)

    with codecs.open(result_dir + user_link_fname + '.new', 'w', 'utf-8') as wd:
        Spider.extractLastHopUsers.cleanUserLinks(user_link_fname,
                                                  'user_links.new', proj_dir, wd)