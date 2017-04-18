"""
Generate Samples from all mini blog.
"""
import os.path
import glob
import codecs
import sys
sys.path.append('..')
import Spider.utils

WINDOW_START = 20170417000
WINDOW_END = 201704182359

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
    for tweet in tweets:
        if tweet.omid == '0' or int(tweet.time) < WINDOW_START or int(tweet.time) > WINDOW_END:
            continue
        last_hop_uid = tweet.getContentLastHop()
        if last_hop_uid == '':
            #bypass incomplete tweet
            continue
        if last_hop_uid:
            if last_hop_uid not in last_hops:
                last_hops[last_hop_uid] = {'mid': [], 'omid': []}
            if tweet.omid not in last_hops[last_hop_uid]['omid']:
                last_hops[last_hop_uid]['omid'].append(tweet.omid)
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
    for last_hop in last_hops.keys():
        if last_hop not in user_tweets:
            user_tweets[last_hop] = Spider.utils.loadTweets(
                '{dir}{uid}.tweet'.format(dir=data_dir, uid=last_hop))
            user_origin_tweets[last_hop] = Spider.utils.loadTweets(
                '{dir}{uid}.original_tweet'.format(dir=data_dir, uid=last_hop))
    for last_hop, mes in last_hops.items():
        pass





def generateSamples(proj_dir):
    data_dir = proj_dir + 'data/'
    res_dir = proj_dir + 'result/'
    users = Spider.utils.loadUsers(data_dir + 'user_links.new')
    user_tweets = dict()
    user_origin_tweets = dict()
    with codecs.open(res_dir + 'sample', 'w','utf-8') as swd:
        for user in users.values():
            generateSampleForUser(user, )

