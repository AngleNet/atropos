import codecs, sys, os.path, glob
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

def getUserActivity(data_dir):
    uids = [os.path.basename(fn).split('.')[0] for fn in glob.glob('{dir}/*.tweet'.format(dir=data_dir))]
    tweets_statis = dict()
    for _uid in uids:
        tweets_statis[_uid] = {
            'nr_otweets': dict(),
            'nr_tweets': 0,
            'nr_retweets': 0,
            'nr_days': 0
        }
        tweets = Spider.utils.loadTweets('{dir}/{uid}.tweet'.format(dir=data_dir, uid=_uid), use_filter=False);
        otweets = Spider.utils.loadTweets('{dir}/{uid}.origin_tweet'.format(
            dir=data_dir, uid=_uid
        ))
        times = list()
        for _tweet in tweets.values():
            times.append(_tweet.time[:8])
            tweets_statis[_uid]['nr_tweets'] += 1
            if _tweet.omid != '0':
                tweets_statis[_uid]['nr_retweets'] += 1
                if _tweet.omid in otweets:
                    _ouid = otweets[_tweet.omid].uid
                    if _ouid not in tweets_statis[_uid]['nr_otweets']:
                        tweets_statis[_uid]['nr_otweets'][_ouid] = 1
                    else:
                        tweets_statis[_uid]['nr_otweets'][_ouid] += 1
        times = sorted(times)
        #tweets_statis[_uid]['nr_days'] = int(times[-1]) - int(times[0]) + 1
        # if tweets_statis[_uid]['nr_days'] < 1:
        #     Spider.utils.debug('Met a wrong time window for {uid}'.format(uid=_uid))
    return tweets_statis

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

    user_activity = getUserActivity(data_dir + '/user_tweets')


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

        if samp.uid not in user_activity:
            Spider.utils.debug('Missing user posting habit for {uid}'.format(
                uid=samp.uid
            ))
        else:
            _samp.retweet_rate = user_activity[samp.uid]['nr_retweets']/float(
                user_activity[samp.uid]['nr_tweets']
            )
            if samp.ouid not in user_activity[samp.uid]['nr_otweets']:
                Spider.utils.debug('Missing user posting habit for last hop {ouid}'.format(
                    ouid=samp.ouid
                ))
            elif user_activity[samp.uid]['nr_retweets'] != 0:
                _samp.interact_rate = user_activity[samp.uid]['nr_otweets'][samp.ouid]/float(
                    user_activity[samp.uid]['nr_retweets']
                )

    with codecs.open('{dir}/samples.train'.format(dir=res_dir), 'w', 'utf-8') as fd:
        for samp in samps.values():
            fd.write(str(samp) + '\n')



