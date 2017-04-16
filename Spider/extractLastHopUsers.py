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

def cleanUserLinks(user_link_fname, user_fname, proj_dir, wd):
    """
    Remove duplicate users and find page id of each user, if the page id
    is not spided yet, dump it to a tmp file.
    :param user_link_fname:
    :param user_fname:
    :param data_dir:
    :param wd:
    :return:
    """
    data_dir = proj_dir+'data/'
    res_dir = proj_dir + 'result/'
    user_fname = data_dir + user_fname
    users = Spider.utils.loadUsers(user_fname)
    user_links = dict()
    with codecs.open(res_dir+user_link_fname, 'r','utf-8') as fd:
        for line in fd.readlines():
            link = Spider.utils.originalUserLinkSpiliter(line)
            if not line:
                continue
            if link.ouid not in user_links:
                user_links[link.ouid] = link
                continue
            if user_links[link.ouid].time == '':
                user_links[link.ouid].time = link.time
            elif link.time != '' and int(link.time) < int(user_links[link.ouid].time):
                user_links[link.ouid].time = link.time
            user_links[link.ouid].omid.extend(link.omid)
    with codecs.open(res_dir+'user_links.no_pid', 'w', 'utf-8') as fd:
        for link in user_links.values():
            if link.ouid in users:
                link.pid = users[link.ouid].page_id
                wd.write(str(link) + '\n')
            else:
                fd.write(str(link) + '\n')

if __name__ == '__main__':
    data_dir = '../data/'
    with codecs.open(data_dir + 'user_links.original', 'w', 'utf-8') as wd:
        extractUser('1884559332', data_dir, wd)