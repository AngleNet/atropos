import codecs
import sys
sys.path.append('..')
import Spider.topicWeiboSpider

import Spider.utils
if __name__ == '__main__':
    data_dir = sys.argv[1]
    Spider.utils.loadSUB(data_dir+'.sub')
    with codecs.open(data_dir + 'topk_topics', 'r', 'utf-8') as fd:
        for line in fd.readlines():
            topic = Spider.utils.topicLineSpliter(line)
            if topic:
                spider = Spider.topicWeiboSpider.TRWeiboSpider()
                Spider.utils.writeList(data_dir + topic.idx, spider.spide(4))