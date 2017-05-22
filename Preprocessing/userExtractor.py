
import sys
sys.path.append('..')
import Spider.utils
import codecs

def loadSamples(fn):
    samps = dict()
    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            samp = Spider.utils.weiboSampleLineSpliter(line)
            if samp and samp.id not in samps:
                samps[samp.id] = samp
    return samps

if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'
    samps = loadSamples(data_dir + '/tweets.sample')
    ousers = Spider.utils.loadUsers(data_dir + '/user_links.new')
    users = dict()
    for samp in samps.values():
        if samp.uid in users and users[samp.uid].page_id != '':
            continue
        if samp.uid in ousers:
            users[samp.uid] = ousers[samp.uid]
        else:
            users[samp.uid] = Spider.utils.User()
            users[samp.uid].id = samp.uid
    fd = codecs.open(res_dir + '/user_links.failed', 'w', 'utf-8')
    od = codecs.open(res_dir + '/user_links.new', 'w', 'utf-8')
    for user in users.values():
        if user.page_id != '':
            od.write(str(user) + '\n')
        else:
            fd.write(str(user) + '\n')