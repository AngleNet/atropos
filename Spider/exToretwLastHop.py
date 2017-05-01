import codecs, sys, glob, os.path
sys.path.append('..')
import Spider.utils

def extractor(data_dir, pid):
    users = dict()
    tweet_fn = '{dir}/{pid}.tweet'.format(dir=data_dir, pid=pid)
    retweet_fn = '{dir}/{pid}.retweet'.format(dir=data_dir, pid=pid)
    if not os.path.exists(tweet_fn) or not os.path.exists(retweet_fn):
        return users
    tweets = Spider.utils.loadTweets(tweet_fn)
    retweets = Spider.utils.loadTweets(retweet_fn)
    for retweet in retweets.values():
        user = Spider.utils.User()
        hop = retweet.getContentLastHop()
        if hop is None:
            if retweet.mid not in tweets:
                Spider.utils.debug('Original weibo {mid} is missing'.format(mid=retweet.mid))
            else:
                user.id = tweets[retweets.mid].uid
        elif hop != ',':
            uid = hop.split(',')[0].strip()
            link = hop.split(',')[1].strip()
            if uid == '' or link == '':
                continue
            else:
                user.id = uid
                user.link = link
        else:
            continue
        if user.id not in users:
            users[user.id] = user
    return users

def extractLastHop(proj_dir):
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'
    pids  = [os.path.basename(fn).split('.')[0] for fn in glob.glob(data_dir + '/*.retweet')]
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