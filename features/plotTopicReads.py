import glob,os.path, faker, datetime
import sys
sys.path.append('../')
import Spider.utils
import codecs
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('qt4agg')
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
plt.rcParams['axes.unicode_minus']=False
import matplotlib.dates as mdates

def getTotalReads(fn):
    with codecs.open(fn, 'r','utf-8') as fd:
        for line in fd.readlines():
            if 'Total_Reads' in line:
                return int(line.split(':')[1])

def randomColors(num):
    fake = faker.Factory.create()
    return [fake.hex_color() for i in range(0, num)]
    pass
if __name__ == '__main__':
    data_dir = '../data'
    dates = sorted([os.path.basename(n).split('.')[0] for n in glob.glob(data_dir+'/*.topk_topic')])
    topics = dict()
    total_reads = list()
    for _d in dates:
        fn = '{dir}/{date}.topk_topic'.format(dir=data_dir,date=_d)
        topics[_d] = [ r.reads for r in Spider.utils.loadTrendingTopics(fn).values()]
        topics[_d] = sorted(topics[_d], reverse=True)
        total_reads.append(getTotalReads(fn))
    topk = 10
    topk_topics = dict()
    for i in range(0, topk):
        topk_topics[i] = list()
    for i in range(0, topk):
        for _date in dates:
            topk_topics[i].append(topics[_date][i])

    x_dates = mdates.drange(
        datetime.datetime(int(dates[0].split('-')[0]), int(dates[0].split('-')[1]),
                          int(dates[0].split('-')[2])),
        datetime.datetime(int(dates[-1].split('-')[0]), int(dates[-1].split('-')[1]),
                          int(dates[-1].split('-')[2])+1),
        datetime.timedelta(days=1)
    )
    plt_ranks = dict()
    colors = randomColors(topk+1)
    fig = plt.figure()
    plt_ranks[0] = plt.bar(x_dates, topk_topics[0], width=0.3, color=colors[0], label='Top-1')
    for _rank in range(1, topk):
        plt_ranks[_rank] = plt.bar(x_dates, topk_topics[_rank], width=0.3,
                                   color=colors[_rank], bottom=topk_topics[_rank-1], label='Top-'+str(_rank+1))
    #plt.plot(x_dates, total_reads, color=colors[-1])
    #plt.legend(tuple(plt_ranks), tuple(['Top-'+str(i) for i in range(1, topk+1)]))
    plt.legend()

    plt.gca().xaxis_date()
    fig.autofmt_xdate()
    plt.show()
