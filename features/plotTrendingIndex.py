import sys
sys.path.append('../')
import Spider.utils
import codecs
import numpy as np
import pylab as plt
# import matplotlib
# import matplotlib.pyplot as plt
# matplotlib.use('qt4agg')
# matplotlib.rcParams['font.sans-serif'] = ['SimHei']
# matplotlib.rcParams['font.family']='sans-serif'
# plt.rcParams['axes.unicode_minus']=False
def loadData(fn):
    pos = list()
    negs = list()
    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            samp = Spider.utils.TrainningSample.lineSpliter(line)
            if not samp:
                continue
            if samp.pos == 1:
                pos.append(samp.trending_index)
            else:
                negs.append(samp.trending_index)
    return (pos, negs)

def load(fn):
    pos = list()
    negs = list()
    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line == '':
                continue
            cols = line.split(',')
            if cols[5] == '1':
                pos.append(float(cols[-1]))
            else:
                negs.append(float(cols[-1]))
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
        if trindex[_seq]['pos'] == 0:
            trindex[last_seq]['pos'] += trindex[_seq]['pos']
            trindex[last_seq]['negs'] += trindex[_seq]['negs']
            del trindex[_seq]
            erase = True
            continue
        last_seq = _seq


    # erase = False
    # for _seq in seq:
    #     if trindex[_seq]['pos'] == 0 and trindex[_seq]['negs'] == 0:
    #         erase = True
    #     if erase  and (trindex[_seq]['pos'] < 4 or trindex[_seq]['negs'] < 4):
    #         del trindex[_seq]
    for _seq in trindex.keys():
        # if trindex[_seq]['pos'] + trindex[_seq]['negs'] == 0:
        #     trindex[_seq] = 0
        #     continue
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
    nr_parts = 90
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
    total = 0
    last_seq = 0
    for _seq in seq:
        if trindex[_seq]['pos'] == 0:
            break
        total += trindex[_seq]['pos']
        if _seq == 0:
            trindex[_seq] = trindex[_seq]['pos']
        else:
            trindex[_seq] = trindex[last_seq] + trindex[_seq]['pos']
        last_seq = _seq
    for _ in seq:
        if _ >= _seq:
            del trindex[_]
    for _seq in sorted(trindex.keys()):
        trindex[_seq] = trindex[_seq]/total
    x = [k for k in sorted(trindex.keys())]
    y = [trindex[k] for k in sorted(trindex.keys())]
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
    total = 0
    last_seq = 0
    for _seq in seq:
        if trindex[_seq]['pos'] == 0:
            break
        total += trindex[_seq]['negs']
        if _seq == 0:
            trindex[_seq] = trindex[_seq]['negs']
        else:
            trindex[_seq] = trindex[last_seq] + trindex[_seq]['negs']
        last_seq = _seq
    for _ in seq:
        if _ >= _seq:
            del trindex[_]
    for _seq in sorted(trindex.keys()):
        trindex[_seq] = trindex[_seq]/total
    x = [k for k in sorted(trindex.keys())]
    y = [trindex[k] for k in sorted(trindex.keys())]
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

    proj_dir = '..'
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'
    pos_data, negs_data  = load('{data_dir}/samples.train'.format(data_dir=data_dir))
    # pos_data, negs_data  = loadData('{data_dir}/samples.train'.format(data_dir=data_dir))
    #Trending Index histogram
    # trindxStatus(pos_data, negs_data)
    x, pos, width = caculateProb(negs_data, pos_data)

    ######################Double X-Window###########
    # x, pos, width= double(x, pos, width)
    font = {'family': 'Times New Roman',
            'weight': 'normal',
            'size': 16,
            }
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
    #############################################
    plt.figure(figsize=(8,6), dpi=80)
    plt_pos = plt.bar(x, pos, width, linewidth=0.2, color='#919191',
                      edgecolor='w')
    plt_neg = plt.bar(x, neg, width, color='#c1c1c1',
                      linewidth=0.1, edgecolor='w', bottom=pos)
    Spider.utils.dumpPlot(dict(
        file='{res_dir}/转发概率.txt'.format(res_dir=res_dir),
        xlabel=dict(label='微博热度值', data=x),
        ylabel=dict(label='转发概率', data=pos)
    ))
    ax =plt.gca()
    ax.spines['right'].set_color('black')
    plt.ylabel(u"Probability", fontdict=font)
    plt.xlabel(u'Weibo-heat', fontdict=font)
    plt.ylim(0, 1.0)
    plt.xlim(0, max(x))
    _ticks = [i*0.0038 for i in range(0, 7)]
    plt.xticks(_ticks, ['{_x:.3f}'.format(_x=i) for i in _ticks], family='Times New Roman')
    _ticks = [i*0.1 for i in range(1, 11)]
    plt.yticks(_ticks, ['{_y:.1f}'.format(_y=i) for i in _ticks], family='Times New Roman')
    font['size'] = 12
    plt.legend((plt_pos[0], plt_neg[0]), ('Repost', 'Ignore'), loc= 'upper right', prop=font)
    plt.savefig('C://Users//anglenet//WeiboGraphs//test//HeatProb.svg')
    plt.show()

    ############CDF Curse###########################


    x, pos, width = cacCumProbPos(negs_data, pos_data)
    plt.figure(figsize=(8,6), dpi=80)
    plt_pos = plt.plot(x, pos, color='black', linestyle='-',  label='Reposting', linewidth=1)
    Spider.utils.dumpPlot(dict(
        file='{res_dir}/CDF-转发.txt'.format(res_dir=res_dir),
        xlabel=dict(label='微博热度值', data=x),
        ylabel=dict(label='转发累积概率', data=pos)
    ))
    x, neg, width = cacCumProbNeg(negs_data, pos_data)
    plt_neg = plt.plot(x, neg,  color='black', linestyle=':', label='Ignoring', linewidth=1)
    Spider.utils.dumpPlot(dict(
        file='{res_dir}/CDF-忽略.txt'.format(res_dir=res_dir),
        xlabel=dict(label='微博热度值', data=x),
        ylabel=dict(label='忽略累积概率', data=neg)
    ))

    plt.ylabel(u"CDF", fontdict=font)
    plt.xlabel(u'Weibo-heat', fontdict=font)
    plt.ylim((0, 1.0))
    plt.xlim(0, max(x))
    _ticks = [0,]
    _ticks.extend([i*0.1 for i in range(1, 11)])
    plt.yticks(_ticks, ['{_y:.1f}'.format(_y=i) for i in _ticks], family='Times New Roman')
    _ticks = [i*0.0038for i in range(1, int(max(x)/0.0038)+1)]
    plt.xticks(_ticks, ['{_x:.3f}'.format(_x=i) for i in _ticks], family='Times New Roman')
    font['size'] = 12
    plt.legend(loc='upper right', bbox_to_anchor=[1.0, 0.97], prop=font)
    plt.savefig('C://Users//anglenet//WeiboGraphs//test//HeatCumu.svg')
    plt.show()

    #The following is used for testing only.
    # x, pos, width = cacCumProbPos(negs_data, pos_data)
    # plt.figure(figsize=(8,6), dpi=80)
    # plt_pos = plt.plot(x, pos, color='#cc0404', label='Repost', linewidth=1.5)
    # Spider.utils.dumpPlot(dict(
    #     file='{res_dir}/CDF-转发.txt'.format(res_dir=res_dir),
    #     xlabel=dict(label='微博热度值', data=x),
    #     ylabel=dict(label='转发累积概率', data=pos)
    # ))
    # x, neg, width = cacCumProbNeg(negs_data, pos_data)
    # plt_neg = plt.plot(x, neg,  color='#27589a', label='Ignore', linewidth=1.5)
    # Spider.utils.dumpPlot(dict(
    #     file='{res_dir}/CDF-忽略.txt'.format(res_dir=res_dir),
    #     xlabel=dict(label='微博热度值', data=x),
    #     ylabel=dict(label='忽略累积概率', data=neg)
    # ))
    # markerline, stemlines, baseline = plt.stem([0.02,], [0.88173913,], linefmt='r:', markerfmt='o', basefmt=':')
    # plt.setp(stemlines, 'linewidth', 1.2)
    # plt.plot([0, 0.02], [0.88173913, 0.88173913], color='red',  linewidth=1.2, linestyle=':')
    # plt.annotate(r'(0.02, 0.88)',
    #      xy=(0.02, 0.88173913), xycoords='data',
    #      xytext=(+5, -10), textcoords='offset points', fontsize=10)
    # ax = plt.gca()
    # plt.ylabel(u"Cumulative Distribution")
    # plt.xlabel(u'Heat')
    # plt.ylim((0, 1.0))
    # plt.xlim(0, 0.045)
    # _ticks = [0,]
    # _ticks.extend([i*0.1 for i in range(1, 11)])
    # plt.yticks(_ticks, ['{_y:.1f}'.format(_y=i) for i in _ticks])
    # _ticks = [i*0.004for i in range(1, 12)]
    # plt.xticks(_ticks, ['{_x:.3f}'.format(_x=i) for i in _ticks])
    # plt.legend(loc='upper right', bbox_to_anchor=[1.0, 0.97])
    # plt.savefig('C://Users//anglenet//WeiboGraphs//trash.eps')
    # plt.show()
    ##################Old Function###################
    # pos_data = trendingIndexFilter(pos_data,bins[-1])
    # neg_data = trendingIndexFilter(negs_data, bins[-1])
    # plt_pos = plt.hist(pos_data, bins, normed=1, histtype='step',
    #                    cumulative=True, label='转发', color='#339194')
    # plt_neg = plt.hist(neg_data, bins, normed=1, histtype='step',
    #                    cumulative=True, label='忽略', color='#fb6b41')
    ###############Old End #########################

