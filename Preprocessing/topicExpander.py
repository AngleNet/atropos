
import sys, glob, os.path, codecs
sys.path.append('..')
import Spider.utils
def expander(pid, proj_dir, topics):
    tweets = Spider.utils.loadTweets('{dir}/data/{pid}.origin_tweet'.format(dir=proj_dir, pid=pid))
    if tweets is None:
        return
    with codecs.open('{dir}/result/{pid}'.format(dir=proj_dir, pid=pid), 'w', 'utf-8') as fd:
        fd.write('{reads},{name}\n'.format(reads=topics[pid].reads, name=topics[pid].name))
        for tweet in tweets.values():
            _, __, txt = tweet.seperateContent()
            fd.write(txt + '\n')
if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'

    pids = [os.path.basename(fn).split('.')[0] for fn in glob.glob(data_dir + '/*.tweet')]
    topics = Spider.utils.loadTrendingTopics('{dir}/trending_topics'.format(dir=data_dir))
    for pid in pids:
        expander(pid, proj_dir, topics)
