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

def generateSamplesForUser(uid, user_tweets, user_origin_tweets, swd, data_dir):
    tweet_path = '{data_dir}{uid}.tweet'.format(data_dir=data_dir, uid=uid)
    origin_tweet_path = '{data_dir}{uid}.origin_tweet'.format(data_dir=data_dir, uid=uid)
    tweets = Spider.utils.getTweets(uid, user_tweets, tweet_path)
    origin_tweets = Spider.utils.getTweets(uid, user_origin_tweets, origin_tweet_path)
    if not tweets or not origin_tweets:
        return
    pos_samps = dict()
    ouser_time = dict() #Upper bound
    for tweet in tweets.values():
        if tweet.omid == '0' or tweet.mid in pos_samps:
            continue
        #Positive sample
        last_hop = tweet.getContentLastHop()
        if last_hop:
            # Last hop is not in origin_tweets. Need to load last_hop
            last_hop = last_hop.split(',')[0]
            if last_hop == '':
                Spider.utils.debug('Missing last hop: {last_hop}'.format(last_hop=last_hop))
                continue
            ouser_tweets = Spider.utils.getTweets(last_hop, user_tweets,
                                                  '{data_dir}{uid}.tweet'.format(
                                                      data_dir=data_dir,
                                                      uid=uid
                                                  ))
            ouser_origin_tweets = Spider.utils.getTweets(last_hop, user_origin_tweets,
                                                         '{data_dir}{uid}.tweet'.format(
                                                             data_dir=data_dir,
                                                             uid=uid
                                                         ))
            otime = 0
            for  otweet in ouser_tweets:
                if otweet.omid == tweet.omid and \
                    otime > int(otweet.time):
                    otime = int(otweet.time)
            if otime == 0:
                Spider.utils.
            if last_hop not in ouser_time:
                ouser_time[last_hop] = otime
            elif ouser_time[last_hop] > otime:
                ouser_time[last_hop] = otime
            samp = Spider.utils.WeiboSample()
            samp.id = tweet.mid
            samp.uid = tweet.uid
            samp.time = tweet.time
            samp.ouid =
        else:
            last_hop = origin_tweets[tweet.omid].uid



def generateSamples(data_dir):
    users = list()
    with codecs.open('{data_dir}user_links.new', 'r', 'utf-8') as fd:
        for line in fd.readlines():
            user = Spider.utils.userLineSpliter(line)
            if user:
                users.append(user)
    user_tweets = dict()
    user_origin_tweets = dict()
    with codecs.open(data_dir + 'samples', 'w', 'utf-8') as swd:
        for user in users:
            generateSamplesForUser(user.id, user_tweets, user_origin_tweets, swd, data_dir)

