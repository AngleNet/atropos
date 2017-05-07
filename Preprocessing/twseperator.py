
import sys,os, os.path, glob
import codecs
sys.path.append('..')
import Spider.utils

def seperate(proj_dir, pid):
    otweet_fn = '{dir}/data/{pid}.origin_tweet'.format(dir=proj_dir, pid=pid)
    tweet_fn = '{dir}/data/{pid}.tweet'.format(dir=proj_dir, pid=pid)
    otweets = Spider.utils.loadTweets(otweet_fn)
    tweets = Spider.utils.loadTweets(tweet_fn)
    user_tweets = dict()
    for tweet in tweets.values():
        if tweet.uid not in user_tweets:
            user_tweets[tweet.uid] = dict()
        user_tweets[tweet.uid][tweet.mid] = tweet
    tweet_template = '{dir}/result/{uid}.tweet'
    otweet_template = '{dir}/result/{uid}.origin_tweet'
    for uid in user_tweets.keys():
        with codecs.open(otweet_template.format(dir=proj_dir, uid=uid), 'a', 'utf-8') as wd:
            for otweet in otweets.values():
                wd.write(str(otweet) + '\n')
        with codecs.open(tweet_template.format(dir=proj_dir, uid=uid), 'a', 'utf-8') as wd:
            for tweet in user_tweets[uid].values():
                wd.write(str(tweet) + '\n')
    with codecs.open('{dir}/result/user_links'.format(dir=proj_dir), 'w','utf-8') as fd:
        for uid in user_tweets.keys():
            user = Spider.utils.User()
            user.id = uid
            fd.write(str(user) + '\n')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'

    pids = [os.path.basename(fn).split('.')[0] for fn in glob.glob(data_dir + '/*.tweet')]
    for pid in pids:
        seperate(proj_dir, pid)
