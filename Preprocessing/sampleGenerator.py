"""
Generate Samples from all mini blog.
"""
import os.path
import glob
import codecs
import sys
sys.path.append('..')
import Spider.utils

def nicknameToUser(nick_link):
    pass

def generateSamplesForUser(uid, user_tweets, swd, data_dir):
    tweet_path = '{data_dir}{uid}.tweet'.format(data_dir=data_dir, uid=uid)
    origin_tweet_path = '{data_dir}{uid}.origin_tweet'.format(data_dir=data_dir, uid=uid)
    if not os.path.exists(tweet_path):
        Spider.utils.debug('{uid}.tweet does\'t exists'.format(uid=uid))
        return
    if not os.path.exists(origin_tweet_path):
        Spider.utils.debug('{uid}.origin_tweet does not exists'.format(uid=uid))
    origin_tweets = Spider.utils.loadTweets(origin_tweet_path)
    origin_time = dict()
    tweets = Spider.utils.loadTweets(tweet_path)
    pos_samp = dict()
    for tweet in tweets.values():
        if tweet.omid == '0':
            continue
        last_hop = tweet.getContentLastHop()
        if last_hop and last_hop.find('http') != -1:
            last_hop = nicknameToUser(last_hop)
            if last_hop not in user_tweets:
                if not os.path.exists('{data_dir}{uid}.tweet'.format(data_dir=data_dir, uid=last_hop)):
                    Spider.utils.debug('Missing tweet for last hop {uid}'.format(uid=last_hop))
                    continue
                else:
                    user_tweets[last_hop] = \
                        Spider.utils.loadTweets('{data_dir}{uid}.tweet'.format(
                            data_dir=data_dir, uid=last_hop
                        ))
            if tweet.omid not in tweets[last_hop]:
                Spider.utils.debug('Mini blog {mid} is missing'.format(mid = tweet.omid))
                continue
            origin = tweets[last_hop][tweet.omid]
        else:
            origin = origin_tweets[tweet.omid]
        if origin.uid not in origin_time:
            origin_time[origin.uid] = int(origin.time)
        elif int(origin.time) < origin_time[origin.uid]:
            origin_time[origin.uid] = int(origin.time)
        samp = Spider.utils.WeiboSample()
        samp.truly_retweeted = 1
        samp.id = tweet.mid
        samp.uid = tweet.uid
        samp.time = tweet.time
        samp.ouid = origin.uid
        samp.otime = origin.time
        samp.num_links, samp.num_videos, samp.text = tweet.seperateContent()


    for  uid, ts in origin_time.items():
        for tweet in user_tweets[uid]:
            if int(tweet.time) < user_tweets[uid]:
                continue
            samp = Spider.utils.WeiboSample()
            if tweet.mid in pos_mid:
                samp.truly_retweeted = 1

def generateSamples(data_dir):
    users = list()
    with codecs.open('{data_dir}user_links.new', 'r', 'utf-8') as fd:
        for line in fd.readlines():
            user = Spider.utils.userLineSpliter(line)
            if user:
                users.append(user)
    user_tweets = dict()
    with codecs.open(data_dir + 'samples', 'w', 'utf-8') as swd:
        for user in users:
            generateSamplesForUser(user.id, user_tweets, swd, data_dir)

