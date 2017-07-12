
import codecs
import os.path
import glob
import Spider.utils
if __name__ == '__main__':
    proj_dir = '..'
    res_dir = proj_dir + '/result'
    data_dir = proj_dir + '/data'
    fnames = glob.glob(data_dir + '/*.topk_topic')
    for fname in fnames:
        _date = os.path.basename(fname).split('.')[0]
        kws_fname = '{data_dir}/{date}.kws.10'.format(data_dir=data_dir,
                                                      date=_date)
        topics = dict()
        total = 0
        with codecs.open(fname, 'r', 'utf-8') as fd:
            for line in fd.readlines():
                if 'Total_Reads' in line:
                    total = int(line.split(':')[-1])
                else:
                    topic = Spider.utils.topicLineSpliter(line)
                    if topic and topic.idx not in topics:
                        topics[topic.idx] = topic
        _topics = dict()
        with codecs.open(kws_fname, 'r', 'utf-8') as fd:
            for line in fd.readlines():
                line = line.strip()
                if line == '':
                    continue
                cols = line.split(',')
                idx = cols[0].strip()
                if idx not in topics:
                    Spider.utils.debug('Missing {idx} in key words'.format(
                        idx=idx
                    ))
                kws = ''
                for _kw in cols[1:]:
                    kws += _kw + ';'
                if kws != '':
                    kws = kws[:-1]
                if idx not in _topics:
                    _topics[idx] = {
                        'kws': kws,
                        'index': int(topics[idx].reads)/total
                    }
        with codecs.open('{res_dir}/{date}.index'.format(res_dir=res_dir, date=_date),
                         'w', 'utf-8') as fd:
            idxs = sorted(_topics.keys(), key=lambda x: _topics[x]['index'])
            for idx in idxs:
                fd.write('{idx},{name},{index},{kws}\n'.format(
                    idx=idx, name=topics[idx].name,
                    index=_topics[idx]['index'], kws=_topics[idx]['kws']
                ))
