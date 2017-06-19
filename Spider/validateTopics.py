import codecs
import sys, glob, os
sys.path.append('..')
import Spider.utils

def checkTopic(tid):
    link = "http://weibo.com/p/" + tid + \
           "?pids=Pl_Third_App__11&current_page=1&page=1" \
           "&ajaxpagelet=1&ajaxpagelet_v6=1"
    ret = Spider.utils.reliableGet(link)
    html = Spider.utils.extractHtmlFromScript(ret.text)
    if html == '':
        return False
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'
    Spider.utils.loadSUB(data_dir + '/.sub')
    topic_fs = glob.glob('{dir}/*.topk_topic'.format(dir=data_dir))
    for topic_fn in topic_fs:
        failed_fd = codecs.open('{res}/{date}.failed'.format(res=res_dir,
                                                             date=os.path.basename(topic_fn)[:10]), 'w', 'utf-8')
        with codecs.open(topic_fn, 'r', 'utf-8') as fd:
            for line in fd.readlines():
                line = line.strip()
                if line == '' or len(line.split(',')) == 1:
                    continue
                if checkTopic(line.split(',')[0]):
                    continue
                failed_fd.write(line)
        failed_fd.close()