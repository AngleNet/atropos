import jieba
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
        line = line.strip()
        if line == '':
            return
        cols = line.split(',')
        if len(cols) == 1:
            self.reads = int(line.split(':')[1])
            return
        tid = cols[0].strip()
        rds = cols[1].strip()
        name = ''
        for k in cols[2:]:
            name += k + ','
        name = name[:-1]
        topic = Spider.utils.Topic()
        topic.idx = tid
        topic.reads = rds
        topic.name = name
        self.topics.append(topic)


class Sample:
    def __init__(self, date, content):
        self.date = date
        self.content = content
    def keywords(self):
        return list(jieba.cut(self.content))

    def __str__(self):
        return self.date + ', ' + self.content

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
        fn = os.path.basename(fn)
        day = fn.split('.')[0]
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
    for topics in topics.values():
        for topic in topics.topics:
            topic.trindex = topic.reads / topics.reads

def loadSamples(proj_dir):
    fn = proj_dir + 'data/tweets.sample'
    samples = list()
    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            weibo = Spider.utils.weiboSampleLineSpliter(line)
            if weibo is None:
                continue
            samples.append(weibo)
    return samples

def cacIndex(samp, topics, kws, stop_words):
    topics = topics[samp.time[:8]]
    topics = sorted(topics.topics, key=lambda x: x.idx)
    tridx = 0
    samp_kws = list(jieba.cut(samp.text))
    samp_kws = [kw for kw in samp_kws if kw.strip() != '' and kw not in stop_words ]
    if len(samp_kws) == 0:
        return 0
    for topic in topics:
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

def weighter(samp, samp_kws, topic, kws):
    if samp.content.find(topic.name) != -1:
        return topic.trindex
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

def trendingIndexExecutor(weibos, topics, kws, fd, stop_words):
    for weibo in weibos:
        #print('Processing: ' + str(samp), end='\n\t')
        index = cacIndex(weibo, topics, kws, stop_words)
        samp = Spider.utils.Sample()
        samp.loadFromWeibo(weibo)
        samp.trindx = index
        fd.write(str(samp) + '\n')
        fd.flush()
        #print('Index: ' + str(index) + '}')

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
        proj_dir = '../'
    else:
        proj_dir = sys.argv[1]
    stop_words = loadStopWords('{proj_dir}resource'.format(proj_dir=proj_dir))
    kws = loadKeywords('{proj_dir}data/topics.kws'.format(proj_dir=proj_dir))
    topics = loadTopics('{proj_dir}data'.format(proj_dir=proj_dir))
    cacTrindex(topics)
    samps = loadSamples(proj_dir)
    with codecs.open('{proj_dir}/result/sample'.format(proj_dir=proj_dir), 'w','utf-8') as wd:
        trendingIndexExecutor(samps, topics, kws, wd, stop_words)
