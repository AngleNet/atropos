
import sys
sys.path.append('..')
import codecs
import Spider.utils

if __name__ == '__main__':
    proj_dir = '..'
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'

    topics = dict()
    with codecs.open('{dir}/topics.csv'.format(dir=data_dir), 'r', 'utf-8') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line == '':
                continue
            cols = line.split(',')
            idx = '100808' + cols[0]
            reads = int(cols[2])
            name = ''
            for _ in cols[3:-1]:
                name += _
            _day = cols[-1][:8]
            _time = cols[-1][8:]

            if _day not in topics:
                topics[_day] = dict()
            if _time not in topics[_day]:
                topics[_day][_time] = list()
            topic = Spider.utils.Topic()
            topic.idx = idx
            topic.name = name
            topic.reads = reads
            topics[_day][_time].append(topic)
    for _day in sorted(topics.keys()):
        for _time in sorted(topics[_day].keys()):
            with codecs.open('{dir}/{ts}.topic'.format(dir=res_dir, ts=_day[:4] + '-' + _day[4:6] + '-' + _day[6:8] + _time + '0000'), 'w', 'utf-8') as fd:
                for _topic in topics[_day][_time]:
                    fd.write(str(_topic) + '\n')











