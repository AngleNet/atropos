import os, codecs
import Spider.utils

def extractUsers(uid, links, ouids, data_dir):
    tweet_fname = uid + '.tweet'
    origin_tweet_fname = uid + '.origin_tweet'
    if not os.path.exists(data_dir+tweet_fname) or \
            not os.path.exists(data_dir+origin_tweet_fname):
        Spider.utils.debug('Missing .tweet or .origin_tweet file of ' + uid)
        return []
    tweets = dict()
    with codecs.open(tweet_fname, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            weibo = Spider.utils.tweetLineSpliter(line)
            if weibo and weibo.mid not in tweets:
                tweets[weibo.mid] = weibo
    origin_tweets = dict()
    with codecs.open(origin_tweet_fname, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            weibo = Spider.utils.tweetLineSpliter(line)
            if weibo and weibo.mid not in origin_tweets:
                origin_tweets[weibo.mid] = weibo
    for tweet in tweets.values():
        if tweet.omid == '0':
            continue
        last_hop = tweet.getContentLastHop()
        if last_hop and last_hop not in links:
            links.append(last_hop)
            continue
        if tweet.omid not in origin_tweets:
            Spider.utils.debug('User %(uid)s missing original user of tweet %(omid)s' %
                  dict(
                      uid = uid,
                      omid = tweet.omid
                  ))
            continue
        else:
            ouids.append(origin_tweets[tweet.omid].uid)

if __name__ == '__main__':
    links = list()
    ouids = list()
    extractUsers('1846632123', links, ouids, '')