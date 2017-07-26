import jieba
import jieba.analyse
import math
import operator
import glob, codecs
import  concurrent.futures
import os.path
import sys
sys.path.append('..')
import traceback
import Spider.utils

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

def loadKeywords(fn):
    kws = dict()
    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line == '':
                continue
            cols = line.split(',')
            tid = cols[0]
            if tid in kws:
                print('Duplicate tid: ' + tid)
                continue
            kws[tid] = list()
            for kw in cols[1:]:
                kws[tid].append(kw.strip())
    return kws

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

def loadStopWords(resource_dir):
    stopw = list()
    with codecs.open('{resource_dir}/chinese_stopwords.txt'.format(
        resource_dir=resource_dir), 'r', 'utf-8') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line == '':
                continue
            if line not in stopw:
                stopw.append(line)
    with codecs.open('{resource_dir}/english_stopwords.txt'.format(
        resource_dir=resource_dir), 'r', 'utf-8') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line == '':
                continue
            if line not in stopw:
                stopw.append(line)
    stopw.append('\n')
    return stopw
def cacTrindex(topics):
    for _topics in topics.values():
        for topic in _topics.topics:
            topic.trindex = int(topic.reads) / _topics.reads

def loadSamples(proj_dir):
    fn = proj_dir + '/data/tweets.sample'
    samples = list()
    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            weibo = Spider.utils.weiboSampleLineSpliter(line)
            if weibo is None:
                continue
            samples.append(weibo)
    return samples

def cacIndex2(samp, topics, kws, stop_words):
    topics = topics[samp.time[:8]]
    topics = sorted(topics.topics, key=lambda x: x.idx)
    tridx = 0
    samp_kws = list(jieba.cut(samp.text))
    samp_kws = [kw for kw in samp_kws if kw.strip() != '' and kw not in stop_words]
    if len(samp_kws) == 0:
        return 0
    for topic in topics:
        if topic.idx not in kws:
            continue
        if samp.text.find(topic.name) != -1:
            tridx += topic.trindex
    return tridx

def cacIndex(samp, topics, kws, stop_words, match_topic_name_only):
    topics = topics[samp.time[:8]]
    topics = sorted(topics.topics, key=lambda x: x.idx)
    tridx = 0
    samp_kws = list(jieba.cut(samp.text))
    samp_kws = [kw for kw in samp_kws if kw.strip() != '' and kw not in stop_words]
    if len(samp_kws) == 0:
        return 0
    for topic in topics:
        if topic.idx not in kws:
            continue
        if samp.text.find(topic.name) != -1:
            tridx += topic.trindex
            continue
        if match_topic_name_only:
            continue
        w = weighter(samp, samp_kws, topic, kws)
        tridx += w
        # if w > 0:
        #     print('weighter: \t' + str(w), end='\n\t')
        #     print('kws:\t' + str(samp_kws), end='\n\t')
        #     print('topic_kws:\t' + str(kws[topic.idx]), end='\n\t')
        # else:
        #     print('weighter: ' + str(w), end='\n\t')
        # time.sleep(3)
    return tridx

def cacIndex3(samp, topics, stop_words):
    topics = topics[samp.time[:8]]
    topics = sorted(topics.topics, key=lambda x: x.idx)
    tridx  = 0
    samp_kws = list(jieba.analyse.extract_tags(samp.text, topK=5))
    samp_kws = [kw for kw in samp_kws if kw.strip() != '' and kw not in stop_words]
    if len(samp_kws) == 0:
        return 0
    for topic in topics:
        if topic.name == '##':
            continue
        if samp.text.find(topic.name) != -1:
            tridx += topic.trindex
            continue
        intersect = list()
        for kw in samp_kws:
            if kw not in intersect:
                intersect.append(kw)
        kws = list(jieba.analyse.extract_tags(topic.name[1:-1]))
        for kw in kws:
            if kw not in intersect:
                intersect.append(kw)
        v1 = list()
        v2 = list()
        for kw in intersect:
            if kw in samp_kws:
                v1.append(1)
            else:
                v1.append(0)
            if kw in kws:
                v2.append(1)
            else:
                v2.append(0)
        tridx += cosSimilarity(v1, v2) * topic.trindex
    return tridx

def weighter(samp, samp_kws, topic, kws):
    intersect = list()
    for kw in samp_kws:
        if kw not in intersect:
            intersect.append(kw)
    for kw in kws[topic.idx]:
        if kw not in intersect:
            intersect.append(kw)
    v1 = list()
    v2 = list()
    for kw in intersect:
        if kw in samp_kws:
            v1.append(1)
        else:
            v1.append(0)
        if kw in kws[topic.idx]:
            v2.append(1)
        else:
            v2.append(0)
    # print('weibo: \t' + str(samp_kws), end='\n\t')
    # print('topic: \t' + str(kws[topic.idx]), end='\n\t')
    # print('Intersection\t: ' + str(intersect), end='\n\t')
    # print('v1: \t' + str(v1), end='\n\t')
    # print('v2: \t' + str(v2), end='\n\t')
    # print('TopicTrendingIndex: ' + str(topic.trindex), end='\n\t')
    return cosSimilarity(v1, v2) * topic.trindex

def dot_product2(v1, v2):
    return sum(map(operator.mul, v1, v2))

def cosSimilarity(v1, v2):
    prod = dot_product2(v1, v2)
    len1 = math.sqrt(dot_product2(v1, v1))
    len2 = math.sqrt(dot_product2(v2, v2))
    if len1 == 0 or len2 == 0:
        import pdb; pdb.set_trace()
        print(str(v1) + ', ' + str(v2))
    return prod / (len1 * len2)

def dump(fn, items):
    with codecs.open(fn, 'w', 'utf-8') as fd:
        for item in items:
            fd.write(str(item) + '\n')
            fd.flush()
    pass

def cacParallel(samps, topics, kws):
    res = list()
    samps = divideList(samps)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = dict()
        i = 0
        for task in samps:
            futures[executor.submit(trendingIndexExecutor(task, topics, kws))] = i
            print('Sumit task  ' + str(i))
            i+=1
        for future in concurrent.futures.as_completed(futures):
            try:
                res.extend(future.result())
            except Exception:
                traceback.print_exc()

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

def executor(weibos, topics, kws, fd, stop_words, users):
    for weibo in weibos:
        #print('Processing: ' + str(samp), end='\n\t')
        # Case1: Expand topics and match weibo contents.
        index = cacIndex(weibo, topics, kws, stop_words, False)
        # Case2: Match weibo and topics fully
        # index = cacIndex(weibo, topics, kws, stop_words, True)
        # Case3: Split topic name and weibo contents.
        # index = cacIndex3(weibo, topics, stop_words)
        ntopics, ntrtopics = containsTopics(weibo, topics)
        samp = Spider.utils.Sample()
        samp.loadFromWeibo(weibo)
        samp.trindex = index
        samp.num_topics = ntopics
        samp.num_trending_topics = ntrtopics
        if samp.uid in users:
            samp.similarity = labelSimilarity(weibo.text, users[samp.uid], stop_words)
        if samp.num_trending_topics == 0:
            samp.has_topics = 0
        else:
            samp.has_topics = 1
        fd.write(str(samp) + '\n')
        fd.flush()
        #print('Index: ' + str(index) + '}')

def labelSimilarity(content, user, stop_words):
    samp_kws = list(jieba.analysis.extract_tags(content, topK=50))
    samp_kws = [kw for kw in samp_kws if kw.strip() != '' and kw not in stop_words]
    if len(samp_kws) == 0:
        return 0
    labels = list()
    for label in user.label.split(';'):
        lbs = list(jieba.analysis.extract_tags(label))
        labels.extend(lbs)
    labels = [kw for kw in labels if kw.strip() != '' and kw not in stop_words]
    intersect = list()
    for kw in samp_kws:
        if kw not in intersect:
            intersect.append(kw)
    for kw in labels:
        if kw not in intersect:
            intersect.append(kw)
    v1 = list()
    v2 = list()
    for kw in intersect:
        if kw in samp_kws:
            v1.append(1)
        else:
            v1.append(0)
        if kw in labels:
            v2.append(1)
        else:
            v2.append(0)
    return cosSimilarity(v1, v2)

def divideList(samps):
    length = len(samps)
    step = 100
    res = list()
    i = 0
    for i in range(0, length//step):
        res.append(samps[i*step: (i+1)*step])
    if i*step != length:
        res.append(samps[i*step:(i+1)*step])
    return res

if __name__ == '__main__':
    if len(sys.argv) == 1:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    stop_words = loadStopWords('{proj_dir}/resource'.format(proj_dir=proj_dir))
    kws = loadKeywords('{proj_dir}/data/topics.kws'.format(proj_dir=proj_dir))
    topics = loadTopics('{proj_dir}/data'.format(proj_dir=proj_dir))
    users = Spider.utils.loadUsers('{proj_dir}/data/users'.format(proj_dir=proj_dir))
    cacTrindex(topics)
    samps = loadSamples(proj_dir)
    with codecs.open('{proj_dir}/result/sample'.format(proj_dir=proj_dir), 'w','utf-8') as wd:
        executor(samps, topics, kws, wd, stop_words, users)