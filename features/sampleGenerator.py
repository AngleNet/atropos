import codecs, sys
sys.path.append('..')
import Spider.utils

def loadWeiboSample(fn):
    samps = dict()
    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            samp = Spider.utils.weiboSampleLineSpliter(line)
            if samp and samp.id not in samps:
                samps[samp.id] = samp
    return samps

def loadTrindexSample(fn):
    samps = dict()
    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            samp = Spider.utils.sampleLineSpliter(line)
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

    weibo_samps = loadWeiboSample(data_dir + '/tweets.sample')
    trdx_samps = loadTrindexSample(data_dir + '/samples.trindex')
    users = Spider.utils.loadUsers(data_dir + '/users')
    samps = dict()

    ntweets = dict()
    nretweets = dict()
    ninteracts = dict()


    for samp in weibo_samps.values():
        _samp = Spider.utils.TrainningSample()
        _samp.id = samp.id
        if samp.ouid != '' and samp.ouid in users:
                _samp.certified = int(users[samp.ouid].isCertified)
                _samp.num_followers = int(users[samp.ouid].follower)
        else:
            Spider.utils.debug('Personal information of user {uid} not found'
                               ', setting to 0'.format(
                uid=samp.ouid
            ))
        _samp.num_urls = int(samp.num_links)
        _samp.num_videos = int(samp.num_videos)
        _samp.content_len = len(samp.text)
        if samp.id in trdx_samps:
            _samp.trending_index = float(trdx_samps[samp.id].trindex)
        else:
            Spider.utils.debug('Trending index of sample {mid} not found'
                               ', setting to 0'.format(mid=samp.id))
            _samp.trending_index = 0.0
        if _samp.id not in samps:
            samps[_samp.id] = _samp
        else:
            Spider.utils.debug('Duplicate sample of {mid}, bypassing'.format(
                mid=samp.id
            ))
        if int(samp.truly_retweeted) == 1:
            _samp.pos = 1

    with codecs.open('{dir}/samples.train'.format(dir=res_dir), 'w', 'utf-8') as fd:
        for samp in samps.values():
            fd.write(str(samp) + '\n')



