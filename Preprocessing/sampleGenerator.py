"""
Generate Samples from all mini blog.

uid, time, ouid, otime, is_pos, text
"""

import codecs
import sys
sys.path.append('..')
import Spider.utils

def getTweets(uid, data_dir, user_tweets, is_origin):
    if is_origin:
        fname = '{dir}/{uid}.origin_tweet'.format(dir=data_dir, uid=uid)
    else:
        fname = '{dir}/{uid}.tweet'.format(dir=data_dir, uid=uid)
    if uid in user_tweets:
        return user_tweets[uid]
    return Spider.utils.loadTweets(fname)

def timeFilter(samp):
    if samp is None:
        return True
    return int(samp.time) < Spider.utils.Config.SAMPLE_WINDOW_START or \
                        int(samp.time)>= Spider.utils.Config.SAMPLE_WINDOW_END

def topicFilter(samp, topics):
    if samp is None:
        return True
    for topic in topics.values():
        if samp.find(topic.name) != -1:
            return False
    return True

def containsTopic(samp):
    if samp is None:
        return False
    text = samp.text
    s = text.find('#')
    if s == -1:
        return False
    t = text[s + 1:].find('#')
    if t == -1:
        return False
    return True
def generateSampleForUser(user, user_tweets, user_origin_tweets, proj_dir, topics):
    pos_samp = dict()
    neg_samp = dict()
    data_dir= proj_dir + '/data'
    if user.id in user_tweets:
        tweets = user_tweets[user.id]
        origin_tweets = user_origin_tweets[user.d]
    else:
        tweets = Spider.utils.loadTweets('/{dir}/{uid}.tweet'.format(dir=data_dir, uid=user.id))
        user_tweets[user.id] = tweets
        origin_tweets = Spider.utils.loadTweets('/{dir}/{uid}.origin_tweet'.format(dir=data_dir, uid=user.id))
        user_origin_tweets[user.id] = origin_tweets
    if tweets is None:
        return (pos_samp, neg_samp)
    last_hops = list()
    for tweet in tweets.values():
        if tweet.omid == '0' or tweet.omid not in origin_tweets:
            continue
        samp = Spider.utils.WeiboSample()
        samp.id = tweet.mid
        samp.uid = tweet.uid
        samp.time = tweet.time
        samp.omid = tweet.omid
        samp.num_links, samp.num_videos, samp.text = \
            origin_tweets[tweet.omid].seperateContent()
        uid = tweet.getContentLastHop()
        if uid is None:
            samp.ouid = origin_tweets[tweet.omid].uid
            samp.otime = origin_tweets[tweet.omid].time
            uid = samp.ouid
        elif uid.split(',')[0] != '':
            uid = uid.split(',')[0]
            samp.ouid = uid
        else:
            continue
        if uid not in last_hops:
            last_hops.append(uid)
        samp.truly_retweeted = 1
        pos_samp[samp.id] = samp
    for hop in last_hops:
        tmp_tweets = getTweets(hop, data_dir, user_tweets, False)
        if tmp_tweets is None:
            continue
        tmp_otweets = getTweets(hop, data_dir, origin_tweets, True)
        for tweet in tmp_tweets.values():
            found = False
            for samp in pos_samp.values():
                if tweet.mid == samp.omid or tweet.omid == samp.omid:
                    samp.otime =tweet.time
                    found = True
                    break
            if found:
                continue
            samp = Spider.utils.WeiboSample()
            samp.id = tweet.mid
            samp.ouid = tweet.uid
            samp.otime = tweet.time
            samp.uid = user.id
            samp.time = tweet.time
            samp.truly_retweeted = 0
            if tweet.omid == '0':
                samp.num_links, samp.num_videos, samp.text = tweet.seperateContent()
            elif tweet.omid in tmp_otweets:
                samp.num_links, samp.num_videos, samp.text = \
                        tmp_otweets[tweet.omid].seperateContent()
            else:
                Spider.utils.debug('omid: {omid} of weibo {mid} for user {uid} is missing'.format(
                    omid = tweet.omid, mid = tweet.mid, uid = tweet.uid
                ))
                continue
            neg_samp[samp.id] = samp
    tmp = list()
    for samp in pos_samp.values():
        if samp.time == '' or timeFilter(samp):
            tmp.append(samp.id)
    for mid in tmp:
        del pos_samp[mid]
    tmp = list()
    for samp in neg_samp.values():
        if timeFilter(samp) or not containsTopic(samp):
            tmp.append(samp.id)
    for mid in tmp:
        del neg_samp[mid]
    return (pos_samp, neg_samp)
def generateSamples(proj_dir, topics):
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'
    users = Spider.utils.loadUsers(data_dir + '/user_links.new')
    user_tweets = dict()
    user_origin_tweets = dict()
    pos_samps = dict()
    neg_samps = dict()
    for user in users.values():
        _pos, _neg =  generateSampleForUser(user, user_tweets, user_origin_tweets, proj_dir, topics)
        Spider.utils.dictExtend(pos_samps, _pos)
        Spider.utils.dictExtend(neg_samps, _neg)

    ratio = 0.2
    if len(pos_samps) < len(neg_samps)*ratio:
        num_pos = len(pos_samps)
        num_neg =int(num_pos/ratio)
    else:
        num_pos = int(len(neg_samps)*ratio)
        num_neg = len(neg_samps)

    with codecs.open(res_dir + '/tweets.sample', 'w','utf-8') as swd:
        keys = [k for k in pos_samps.keys()]
        for k in keys[:num_pos]:
            swd.write(str(pos_samps[k]) + '\n')
        keys = [k for k in neg_samps.keys()]
        for k in keys[:num_neg]:
            swd.write(str(neg_samps[k]) + '\n')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    topics = Spider.utils.loadTrendingTopics('{dir}/data/trending_topics'.format(dir=proj_dir))
    generateSamples(proj_dir, topics)
