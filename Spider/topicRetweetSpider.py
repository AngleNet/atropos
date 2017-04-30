import sys
import codecs
sys.path.append('..')
import Spider.utils
if __name__ == '__main__':
    if len(sys.argv) == 1:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    data_dir = proj_dir + '/data'
    result_dir = proj_dir + '/result'

    topics = dict()
    with codecs.open(data_dir+'/trending_topics', 'r', 'utf-8') as fd:
        for line in fd.readlines():
            topic = Spider.utils.topicLineSpliter(line)
            if topic and topic.idx not in topics:
                topics[topic.idx] = topic
    for topic in topics.values():
        spider = topicWeiboSpider()
        spider.start()
        spider.stop()

