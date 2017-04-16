import os, codecs
import Spider.utils

def extractUser(uid, data_dir, wd):
    """
    Extract last hop user and write that link information to wd.
    :param uid:
    :param data_dir:
    :param wd:
    :return:
    """
    tweet_fname = data_dir + uid + '.tweet'
    origin_tweet_fname = data_dir + uid + '.origin_tweet'
    tweets = Spider.utils.loadTweets(tweet_fname)
    origin_tweets = Spider.utils.loadTweets(origin_tweet_fname)
    for tweet in tweets.values():
        if tweet.omid == '0':
            continue
        last_hop = tweet.getContentLastHop()
        #uid, link
        ouser_link = Spider.utils.OriginalUserLink()
        if last_hop:
            cols = last_hop.split(',')
            bypass = False
            for col in cols:
                if col.strip() == '':
                    Spider.utils.debug('last hop has empty fields: {uid}'.format(uid=tweet.uid))
                    bypass = True
                    break
            if bypass:
                continue
            if len(cols) < 2:
                Spider.utils.debug('Wrong last hop: {last_hop} '
                                   'extracted from tweet: {tweet}'.format(last_hop=last_hop,
                                                                          tweet=str(tweet)))
                continue
            ouser_link.ouid = cols[0]
            ouser_link.link = cols[1]
            ouser_link.omid.append(tweet.omid)
        elif tweet.omid in origin_tweets:
            origin_tweet = origin_tweets[tweet.omid]
            ouser_link.ouid = origin_tweet.uid
            ouser_link.link= ''
            ouser_link.time = origin_tweet.time
        else:
            Spider.utils.debug(
                'original weibo {omid} of weibo {mid} is not found, there must'
                'be a bug in userWeiboSpider'.format(omid=tweet.omid, mid=tweet.mid))
        wd.write(str(ouser_link) + '\n')

def extractUsers(uid, links, ouids, data_dir):
    tweet_fname = data_dir + uid + '.tweet'
    origin_tweet_fname = data_dir + uid + '.origin_tweet'
    if not os.path.exists(tweet_fname) or \
            not os.path.exists(origin_tweet_fname):
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