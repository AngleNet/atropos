import codecs
import sys
import glob
import os.path
sys.path.append('..')
import Spider.extractLastHopUsers

import Spider.utils
if __name__ == '__main__':
    data_dir = sys.argv[1]
    users = dict()
    with codecs.open(data_dir + 'user_links.new', 'r', 'utf-8') as fd:
        for line in fd.readlines():
            user = Spider.utils.userLineSpliter(line)
            if user and user.id not in users:
                users[user.id] = user
    uids = list()
    links = list()
    crawled_uids = [os.path.basename(n).split('.')[0] for n in glob.glob(data_dir + '*.tweet')]
    for uid in crawled_uids:
        Spider.extractLastHopUsers.extractUsers(uid, links, uids, data_dir)
    Spider.utils.writeList(data_dir+'user_links.original', links)
    Spider.utils.writeList(data_dir+'user_ids.original', uids)