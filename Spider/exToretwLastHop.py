import codecs, sys, glob, os.path
sys.path.append('..')
import Spider.utils

def extractor(data_dir, pid):
    users = dict()
    tweet_fn = '{dir}/{pid}.origin_tweet'.format(dir=data_dir, pid=pid)
    retweet_fn = '{dir}/{pid}.tweet'.format(dir=data_dir, pid=pid)
    if not os.path.exists(tweet_fn) or not os.path.exists(retweet_fn):
        return users
    otweets = Spider.utils.loadTweets(tweet_fn)
    tweets = Spider.utils.loadTweets(retweet_fn)
    for tweet in tweets.values():
        user = Spider.utils.User()
        hop = tweet.getContentLastHop()
        if hop is None:
            if tweet.omid not in otweets:
                Spider.utils.debug('Original weibo {mid} is missing'.format(mid=tweet.mid))
                continue
            else:
                user.id = otweets[tweet.omid].uid
        elif hop != ',':
            uid = hop.split(',')[0].strip()
            link = hop.split(',')[1].strip()
            if uid == '' or link == '':
                continue
            else:
                user.id = uid
                user.link = link
        else:
            Spider.utils.debug('Bypassing {str}'.format(str=str(tweet)))
            continue
        if user.id not in users:
            users[user.id] = user
    return users

def extractLastHop(proj_dir):
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'
    pids  = [os.path.basename(fn).split('.')[0] for fn in glob.glob(data_dir + '/*.tweet')]
    users = dict()
    for pid in pids:
        Spider.utils.dictExtend(users, extractor(data_dir, pid))
    with codecs.open(res_dir + '/user_links.new', 'w', 'utf-8') as fd:
        for user in users.values():
            fd.write(str(user) + '\n')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    extractLastHop(proj_dir)