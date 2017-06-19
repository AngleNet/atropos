import sys, glob, os, codecs
sys.path.append('..')
import Spider.utils

if __name__ == '__main__':
    proj_dir='..'
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'
    fname = glob.glob('{dir}/*.topk_topic'.format(dir=data_dir))
    if len(fname) != 1:
        Spider.utils.debug('Can not process multiple topk topics a time')
        os._exit(0)
    fname = fname[0]
    _date = os.path.basename(fname).split('.')[0]
    topics  = dict()
    with codecs.open(fname, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            topic = Spider.utils.topicLineSpliter(line)
            if topic and topic.idx not in topics:
                topics[topic.idx] = dict()
                topics[topic.idx]['topic'] = topic
    with codecs.open('{dir}/topics.kws'.format(dir=data_dir), 'r', 'utf-8') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line == '':
                continue
            cols = line.split(',')
            idx = cols[0]
            if idx not in topics:
                Spider.utils.debug('Topic {idx} does not exist'.format(idx=idx))
                continue
            kws = ''
            for _kw in cols[1:]:
                kws += _kw + ','
            if len(kws) > 1:
                kws = kws[:-1]
            topics[idx]['kws'] = kws
    sorted_keys = sorted(topics.keys(), key=lambda idx: topics[idx]['topic'].reads, reverse=True)
    START = 50
    END = 150
    STEP = 20
    for _num in range(START, END+1, STEP):
        _tfd = codecs.open('{dir}/{date}.topk_topic.{num}'.format(
            dir=res_dir, date=_date, num=_num
        ), 'w', 'utf-8')
        _kfd = codecs.open('{dir}/topics.kws.{num}'.format(
            dir=res_dir, num=_num
        ), 'w', 'utf-8')
        __num = 0
        for _idx in sorted_keys:
            if __num >= _num:
                break
            _tfd.write(str(topics[_idx]['topic']) + '\n')
            _kfd.write(str(topics[_idx]['kws']) + '\n')
            __num += 1
        _tfd.close()
        _kfd.close()

