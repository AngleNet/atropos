import glob,os.path, faker, datetime, re
import numpy as np
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

    plt_ranks = dict()
    colors = randomColors(topk+1)
    fig = plt.figure()
    plt_ranks[0] = plt.bar(np.arange(0, len(dates)*0.4, 0.4), topk_topics[0], width=0.2, color=colors[0], label='Top-1')
    cum = [0 for i in range(0, len(dates))]
    for _rank in range(1, topk):
        cum = [cum[i] + topk_topics[_rank][i]for i in range(0, len(dates))]
        plt_ranks[_rank] = plt.bar(np.arange(0, len(dates)*0.4, 0.4), topk_topics[_rank], width=0.2,
                                   color=colors[_rank], bottom=cum, label='Top-'+str(_rank+1))
    plt.legend(loc=1, fontsize='xx-small')
    plt.ylabel('阅读量')
    plt.xlabel('时间')
    plt.title('热点话题阅读量')
    plt.xlim([0, 0.4*len(dates)])
    plt.xticks(np.arange(0.1, len(dates)*0.4, 0.4), [re.sub('-', '/', d)[6:] for d in dates])
    plt.show()
