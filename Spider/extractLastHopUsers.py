import os
import Spider.utils
def extractUsers(uid, data_dir):
    tweet_fname = uid + '.tweet'
    origin_tweet_fname = uid + '.origin_tweet'
    if not os.path.exists(data_dir+tweet_fname) or \
            not os.path.exists(data_dir+origin_tweet_fname):
        Spider.utils.debug('Missing .tweet or .origin_tweet file of ' + uid)
        return []
    tweet