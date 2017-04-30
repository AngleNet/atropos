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
def loadData(fn):
    pos = list()
    negs = list()
    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            samp = Spider.utils.sampleLineSpliter(line)
            if not samp:
                continue
            if samp.truly_retweeted == '1':
                pos.append(float(samp.trindex))
            elif samp.truly_retweeted == '0':
                negs.append(float(samp.trindex))
            else:
                Spider.utils.debug('Missing sample type')
    return (pos, negs)

def caculateProb(negs, pos):
    seq, width = sequence(negs, pos)
    trindex = dict()
    for _seq in seq:
        trindex[_seq] = {
            'negs': 0,
            'pos': 0
        }
    for neg in negs:
        idx = match(seq, neg)
        trindex[idx]['negs'] += 1
    for _pos in pos:
        idx = match(seq, _pos)
        trindex[idx]['pos'] += 1
    erase = False
    last_seq = 0
    for _seq in seq:
        if erase:
            trindex[last_seq]['pos'] += trindex[_seq]['pos']
            trindex[last_seq]['negs'] += trindex[_seq]['negs']
            del trindex[_seq]
            continue
        if trindex[_seq]['pos'] == 0 or trindex[_seq]['negs'] == 0:
            trindex[last_seq]['pos'] += trindex[_seq]['pos']
            trindex[last_seq]['negs'] += trindex[_seq]['negs']
            del trindex[_seq]
            erase = True
            continue
        last_seq = _seq
    for _seq in trindex.keys():
        trindex[_seq] = trindex[_seq]['pos'] / (trindex[_seq]['pos'] + trindex[_seq]['negs'])
    x = [k for k in sorted(trindex.keys())]
    y = [trindex[_x] for _x in x]
    return (x, y, width)
def _caculateCDF(negs, pos, isNeg):
    seq, width = sequence(negs, pos)
    trindex = dict()
    for _seq in seq:
        trindex[_seq] = {
            'negs': 0,
            'pos': 0
        }
    for neg in negs:
        idx = match(seq, neg)
        trindex[idx]['negs'] += 1
    for _pos in pos:
        idx = match(seq, _pos)
        trindex[idx]['pos'] += 1

    erase = False
    for _seq in seq:
        if trindex[_seq]['pos'] == 0 or trindex[_seq]['negs'] == 0 or erase:
            del trindex[_seq]
            erase = True
            continue
    ###Cumulate
    x = [k for k in sorted(trindex.keys())]
    last = None
    for _x in x:
        if last == None:
            last = trindex[_x]
        else:
            trindex[_x]['negs'] += last['negs']
            trindex[_x]['pos'] += last['pos']
            last = trindex[_x]
    for _x in x:
        if isNeg:
            trindex[_x] = trindex[_x]['negs'] / (trindex[_x]['pos'] +
                                                 trindex[_x]['negs'])
        else:
            trindex[_x] = trindex[_x]['pos'] / (trindex[_x]['pos'] +
                                                 trindex[_x]['negs'])
    y = [trindex[_x] for _x in x]
    return (x, y)

def match(seq, samp):
    for i in range(0, len(seq)):
        if i == (len(seq)-1):
            return seq[i]
        if samp >= seq[i] and samp < seq[i+1]:
            return seq[i]

def sequence(negs, pos):
    _max = max((max(negs), max(pos)))
    nr_parts = 100
    step = _max / nr_parts
    seq = [i*step for i in range(0, nr_parts)]
    return (seq, step)
def trendingIndexFilter(data, _max):
    res = list()
    for item in data:
        if item <  _max:
            res.append(item)
    return res


def double(x, pos, width):
    _x = list()
    _pos = list()
    idx = 0
    for idx in range(0, len(x)):
        if idx % 2 == 0:
            _x.append(x[idx])
            if len(x) - 1 == idx:
                _pos.append(pos[idx])
            else:
                _pos.append(pos[idx] + pos[idx+1])
    return (_x, _pos, width*2)

def cacCumProbPos(negs, pos):
    seq, width = sequence(negs, pos)
    trindex = dict()
    for _seq in seq:
        trindex[_seq] = {
            'negs': 0,
            'pos': 0
        }
    for neg in negs:
        idx = match(seq, neg)
        trindex[idx]['negs'] += 1
    for _pos in pos:
        idx = match(seq, _pos)
        trindex[idx]['pos'] += 1
    erase = False
    total = 0
    last_seq = 0
    for _seq in seq:
        total += trindex[_seq]['pos']
        if _seq == 0:
            trindex[_seq] = trindex[_seq]['pos']
        else:
            trindex[_seq] = trindex[last_seq] + trindex[_seq]['pos']
        last_seq = _seq
    for _seq in seq:
        trindex[_seq] = trindex[_seq]/total
    x = [k for k in sorted(trindex.keys())]
    y = [trindex[_x] for _x in x]
    return (x, y, width)
def cacCumProbNeg(negs, pos):
    seq, width = sequence(negs, pos)
    trindex = dict()
    for _seq in seq:
        trindex[_seq] = {
            'negs': 0,
            'pos': 0
        }
    for neg in negs:
        idx = match(seq, neg)
        trindex[idx]['negs'] += 1
    for _pos in pos:
        idx = match(seq, _pos)
        trindex[idx]['pos'] += 1
    erase = False
    total = 0
    last_seq = 0
    for _seq in seq:
        total += trindex[_seq]['negs']
        if _seq == 0:
            trindex[_seq] = trindex[_seq]['negs']
        else:
            trindex[_seq] = trindex[last_seq] + trindex[_seq]['negs']
        last_seq = _seq
    for _seq in seq:
        trindex[_seq] = trindex[_seq]/total
    x = [k for k in sorted(trindex.keys())]
    y = [trindex[_x] for _x in x]
    return (x, y, width)

def trindxStatus(pos, negs):
    data = list()
    data.extend(pos)
    data.extend(negs)
    pyplot = plt
    pyplot.hist(data, 20)

    pyplot.xlabel('Length')
    pyplot.ylabel('Frequency')
    pyplot.title('Trending Topic')
    pyplot.show()
    import os
    os.abort()

if __name__ == '__main__':
    pos_data, negs_data  = loadData('../data/sample')
    #Trending Index histogram
    #trindxStatus(pos_data, negs_data)
    x, pos, width = caculateProb(negs_data, pos_data)

    ######################Double X-Window###########
    x, pos, width= double(x, pos, width)
    neg = [1 - y for y in pos]
    ##############################################
    # fig, pos_axe = plt.subplots()
    # fig.subplots_adjust(right=0.75)
    # neg_axe = pos_axe.twiny()
    # neg_axe.spines['top'].set_visible(True)
    # pos_axe.bar(x, y,  width, color='w', label=u"转发", linewidth=1, hatch='//',linestyle='--')
    # y = [1 - _y for _y in y]
    # neg_axe.bar(x, y, width, color='w', label=u"忽略", linewidth=1, hatch='\\\\', linestyle='--')
    # plt.show()
    ##############################################
    plt.figure()
    plt_pos = plt.bar(x, pos, width, color='#339194', linewidth=0.2,
                      edgecolor='w')
    plt_neg = plt.bar(x, neg, width, color='#fb6b41',
                      linewidth=0.2, edgecolor='w', bottom=pos)

    # plt.title('X: Num Of Retweets Y:  Retweet Probability')
    #plt.grid(True)
    plt.ylabel(u"转发概率")
    plt.xlabel(u'微博热度')
    plt.ylim((0, 1.0))
    plt.xlim(0, max(x))
    plt.legend((plt_pos[0], plt_neg[0]), ('转发', '忽略'))
    plt.show()

    ############CDF Curse###########################

    x, pos, width = cacCumProbPos(negs_data, pos_data)
    plt_pos = plt.plot(x, pos, color='#339194', label='转发')
    x, neg, width = cacCumProbNeg(negs_data, pos_data)
    plt_neg = plt.plot(x, neg,  color='#fb6b41', label='忽略')
    ##################Old Function###################
    # pos_data = trendingIndexFilter(pos_data,bins[-1])
    # neg_data = trendingIndexFilter(negs_data, bins[-1])
    # plt_pos = plt.hist(pos_data, bins, normed=1, histtype='step',
    #                    cumulative=True, label='转发', color='#339194')
    # plt_neg = plt.hist(neg_data, bins, normed=1, histtype='step',
    #                    cumulative=True, label='忽略', color='#fb6b41')
    ###############Old End #########################
    plt.ylabel(u"累积概率")
    plt.xlabel(u'微博热度')
    plt.ylim((0, 1.0))
    plt.xlim(0, max(x))
    plt.legend()
    plt.show()

