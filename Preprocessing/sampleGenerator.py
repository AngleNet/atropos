"""
Generate Samples from all mini blog.

uid, time, ouid, otime, is_pos, text
"""

import codecs
import sys
sys.path.append('..')
import Spider.utils

def generateSampleForUser(user, user_tweets, user_origin_tweets, proj_dir, swd):
    data_dir= proj_dir + 'data_dir/'
    res_dir = proj_dir + 'res_dir/'
    if user.id in user_tweets:
        tweets = user_tweets[user.id]
        origin_tweets = user_origin_tweets[user.d]
    else:
        tweets = Spider.utils.loadTweets('{dir}{uid}.tweet'.format(dir=data_dir, uid=user.id))
        user_tweets[user.id] = tweets
        origin_tweets = Spider.utils.loadTweets('{dir}{uid}.origin_tweet'.format(dir=data_dir, uid=user.id))
        user_origin_tweets[user.id] = origin_tweets

    last_hops = dict()
    pos_samps = dict()
    for tweet in tweets.values():
        if tweet.omid == '0':
            continue
        last_hop = tweet.getContentLastHop()
        if last_hop is not None and last_hop.split(',')[0] == '':
            #bypass incomplete tweet
            continue
        if last_hop is not None and last_hop.split(',')[0] != '':
            last_hop_uid = last_hop.split(',')[0]
        else:
            last_hop_uid = None
        samp = Spider.utils.WeiboSample()
        samp.id = tweet.mid
        samp.uid = tweet.uid
        samp.time = tweet.time
        samp.truly_retweeted = 1
        if tweet.omid == '':
            samp.num_links, samp.num_videos, samp.text = tweet.seperateContent()
        else:
            samp.num_links, samp.num_videos, samp.text = \
                origin_tweets[tweet.omid].seperateContent()

        if last_hop_uid:
            if last_hop_uid not in last_hops:
                last_hops[last_hop_uid] = {'mid': [], 'omid': []}
            if tweet.omid not in last_hops[last_hop_uid]['omid']:
                last_hops[last_hop_uid]['omid'].append(tweet.omid)
            samp.ouid = last_hop_uid
        else:
            if tweet.omid not in origin_tweets:
                Spider.utils.debug('Missing original weibo {omid} of weibo {mid} of user {uid}'.format(
                    omid=tweet.omid, mid = tweet.mid, uid = tweet.uid
                ))
                continue
            if origin_tweets[tweet.omid].uid not in last_hops:
                last_hops[last_hop_uid] = {'mid': [], 'omid': []}
            if tweet.omid not in last_hops[last_hop_uid]['mid']:
                last_hops[last_hop_uid]['mid'].append(tweet.omid)
            samp.ouid = origin_tweets[tweet.omid].uid
            samp.otime = origin_tweets[tweet.omid].time
        swd.write(str(samp) + '\n')
    for last_hop in last_hops.keys():
        if last_hop not in user_tweets:
            user_tweets[last_hop] = Spider.utils.loadTweets(
                '{dir}{uid}.tweet'.format(dir=data_dir, uid=last_hop))
            user_origin_tweets[last_hop] = Spider.utils.loadTweets(
                '{dir}{uid}.original_tweet'.format(dir=data_dir, uid=last_hop))
    for last_hop, mids in last_hops.items():
        least = Spider.utils.Config.SAMPLE_WINDOW_END
        pos_mids = list()
        for mid in mids['mid']:
            if mid not in user_tweets[last_hop]:
                Spider.utils.debug('weibo {mid} of user {uid} is missing'.format(
                    mid = mid, uid = last_hop
                ))
                continue
            if int(user_tweets[last_hop][mid].time) < least:
                least = int(user_tweets[last_hop][mid].time)
            if mid not in pos_mids:
                pos_mids.append(mid)
        for tweet in user_tweets[last_hop].values():
            if tweet.omid in mids['omid']:
                if int(tweet.time) < least:
                    least = int(tweet.tiem)
                if tweet.mid not in pos_mids:
                    pos_mids.append(tweet.mid)
        for tweet in user_tweets[last_hop].values():
            if int(tweet.time) < least or tweet.mid in pos_mids:
                continue
            samp = Spider.utils.WeiboSample()
            samp.id = tweet.mid
            samp.uid = user.id
            samp.time = tweet.time
            samp.ouid = tweet.uid
            samp.otime = tweet.time
            samp.truly_retweeted = 0
            if tweet.omid == '':
                samp.num_links, samp.num_videos, samp.text = tweet.seperateContent()
            else:
                samp.num_links, samp.num_videos, samp.text = \
                    origin_tweets[tweet.omid].seperateContent()
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
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    generateSamples(proj_dir)
