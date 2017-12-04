
import Spider.utils
import codecs
import glob
import os
class TopicsPerDay:
    def __init__(self):
        self.topics = list()
        self.reads = 0
    def add(self, line):
        topic = Spider.utils.topicLineSpliter(line)
        if 'Total_Reads' in line:
            self.reads = int(line.split(':')[-1])
        if topic:
            self.topics.append(topic)
def loadSamples(fn):
    samples = list()
    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            weibo = Spider.utils.weiboSampleLineSpliter(line)
            if weibo is None:
                continue
            samples.append(weibo)
    return samples

def loadTopics(data_dir):
    fs = glob.glob(data_dir + '/*.topk_topic')
    topics = dict()
    for fn in fs:
        day = os.path.basename(fn).split('.')[0]
        day = day[:4] + day[5:7] + day[8:10]
        topics[day] = TopicsPerDay()
        with codecs.open(fn, 'r', 'utf-8') as fd:
            for line in fd.readlines():
                line = line.strip()
                if line == '':
                    continue
                topics[day].add(line)
    return topics
def containsTopics(weibo, topics):
    _content = weibo.text
    names= list()
    if len(_content) > 1:
        _s = _content.find('#')
        while _s != -1:
            _t = _content[_s+1:].find('#')
            if _t != -1:
                names.append(_content[_s:_s+2+_t])
                _content = _content[_s+2+_t:]
                _s = _content.find('#')
            else:
                break
    ntrtopics = 0
    if weibo.time[:8] not in topics:
        Spider.utils.debug('Missing topic information for {date}'.format(date=weibo.time[:8]))
        return (len(names), ntrtopics)
    for _topic in topics[weibo.time[:8]].topics:
        if _topic.name in names:
            ntrtopics += 1
    return (len(names), ntrtopics)
def executor(weibos, topics):
    num_repost = 0
    num_post = 0
    num_topics = dict(pos=0, neg=0)
    num_trtopcis = dict(pos=0, neg=0)
    for weibo in weibos:
        ntopics, ntrtopics = containsTopics(weibo, topics)
        if int(weibo.truly_retweeted) > 0:
            if ntopics > 0:
                num_topics['pos'] += 1
            if ntrtopics >0:
                num_trtopcis['pos'] += 1
            num_repost += 1
        else:
            if ntopics > 0:
                num_topics['neg'] += 1
            if ntrtopics > 0:
                num_trtopcis['neg'] += 1
            num_post += 1
    print('Number of repost: %d, number of post: %d' % (num_repost, num_post))
    print('%.2f of repost contains topics, %.2f of repost contains trending topics' %(num_topics['pos']/num_repost, num_trtopcis['pos']/num_repost))
    print('%.2f of post contains topics, %.2f of post contains trending topics' % (num_topics['neg']/num_post, num_trtopcis['neg']/num_post))



if __name__ == '__main__':
    samples = loadSamples('../data/tweets.sample')
    topics = loadTopics('../data')
    executor(samples, topics)




