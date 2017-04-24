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
        fname = '{dir}{uid}.origin_tweet'.format(dir=data_dir, uid=uid)
    else:
        fname = '{dir}{uid}.tweet'.format(dir=data_dir, uid=uid)
    if uid in user_tweets:
        return user_tweets[uid]
    return Spider.utils.loadTweets(fname)

def timeFilter(samp):
    if samp is None:
        return
    return samp.time < Spider.utils.Config.SAMPLE_WINDOW_START or \
                        samp.time >= Spider.utils.Config.SAMPLE_WINDOW_END

def generateSampleForUser(user, user_tweets, user_origin_tweets, proj_dir, swd):
    data_dir= proj_dir + 'data/'
    if user.id in user_tweets:
        tweets = user_tweets[user.id]
        origin_tweets = user_origin_tweets[user.d]
    else:
        tweets = Spider.utils.loadTweets('{dir}{uid}.tweet'.format(dir=data_dir, uid=user.id))
        user_tweets[user.id] = tweets
        origin_tweets = Spider.utils.loadTweets('{dir}{uid}.origin_tweet'.format(dir=data_dir, uid=user.id))
        user_origin_tweets[user.id] = origin_tweets
    if tweets is None:
        return
    pos_samp = dict()
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
        elif uid != '':
            samp.ouid = uid
        else:
            continue
        if uid not in last_hops:
            last_hops.append(uid)
        samp.truly_retweeted = 1
        pos_samp[samp.id] = samp
    neg_samp = dict()
    for hop in last_hops:
        tmp_tweets = getTweets(hop, data_dir, user_tweets, False)
        if tmp_tweets is None:
            continue
        tmp_otweets = getTweets(hop, data_dir, origin_tweets, True)
        for tweet in tmp_tweets.values():
            found = False
            for samp in pos_samp:
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
        if timeFilter(samp):
            tmp.append(samp.id)
    for mid in tmp:
        del neg_samp[mid]
    for samp in pos_samp.values():
        swd.write(str(samp) + '\n')
    for samp in neg_samp.values():
        swd.write(str(samp) + '\n')

def generateSamples(proj_dir):
    data_dir = proj_dir + 'data/'
    res_dir = proj_dir + 'result/'
    users = Spider.utils.loadUsers(data_dir + 'user_links.new')
    user_tweets = dict()
    user_origin_tweets = dict()
    with codecs.open(res_dir + 'sample', 'w','utf-8') as swd:
        for user in users.values():
            generateSampleForUser(user, user_tweets, user_origin_tweets, proj_dir, swd)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        proj_dir = '../'
    else:
        proj_dir = sys.argv[1]
    generateSamples(proj_dir)
