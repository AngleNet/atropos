import codecs
import sys
sys.path.append('..')
import Spider.topicWeiboSpider

import Spider.utils
if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'
    Spider.utils.loadSUB(data_dir+'/.sub')
    with codecs.open(data_dir + '/topk_topics', 'r', 'utf-8') as fd:
        for line in fd.readlines():
            topic = Spider.utils.topicLineSpliter(line)
            if topic:
                spider = Spider.topicWeiboSpider.TRWeiboSpider(topic)
                Spider.utils.writeList('{dir}/{idx}'.format(dir=data_dir, idx=topic.idx) ,spider.spide(4))