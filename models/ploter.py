import numpy as np
import codecs
import matplotlib.pyplot  as plt

def loadData(dir, fname):
    fname = dir  + '/' +  fname
    dataset = dict(x = list(), y = list())
    with codecs.open(fname, 'r', 'utf-8') as fd:
        fd.readline()
        for line in fd.readlines():
            x, y = line.split(',')
            dataset['x'].append(float(x))
            dataset['y'].append(float(y))
    return dataset

def loadCSV(dir, fname):
    fname = dir  + '/' +  fname
    trending = dict(x = list(), y = list())
    base = dict(x = list(), y = list())
    dataset = dict(trending = trending, base = base)
    with codecs.open(fname, 'r', 'utf-8') as fd:
        fd.readline()
        for line in fd.readlines():
            x, t, b = line.split(',')
            dataset['trending']['x'].append(float(x))
            dataset['trending']['y'].append(float(t))
            dataset['base']['x'].append(float(x))
            dataset['base']['y'].append(float(b))
    return dataset


def perfPlot(base_dataset, better_dataset):
    font = {'family': 'Times New Roman',
            'weight': 'normal',
            'size': 16,
            }
    # LR
    # xs = [0.2, 0.514]
    # ys = [0.6, 0.8]
    # perf = [0.7013, 0.7265]
    # xycoor = [(+8, -4),(-75, +8)]

    # Bayes
    # xs = [0.2, 0.480]
    # ys = [0.467, 0.8]
    # perf = [0.7000, 0.7300]
    # xycoor = [(+8, -4),(-75, +8)]

    # SVM
    xs = [0.2, 0.5350]
    ys = [0.6042, 0.8]
    perf = [0.7000, 0.7300]
    xycoor = [(+8, -4), (-75, +8)]

    plt.figure(figsize=(8, 6), dpi=80)
    plt.plot(better_dataset['x'], better_dataset['y'], linestyle='-', color='black', lw=1.5)
    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6))
    for idx in range(0, 2):
        markerline, stemlines, baseline = plt.stem([xs[idx], ], [ys[idx], ], linefmt='k:', markerfmt='ko',basefmt=':', linewidth=1.2)
        plt.setp(stemlines, 'linewidth', 1.2)
        plt.plot([0, xs[idx]], [ys[idx], ys[idx]], color='black', linewidth=1.2, linestyle=':')
        plt.annotate(r'({_x:.3f}, {_y:.3f})'.format(_x=xs[idx], _y=ys[idx]),
                     xy=(xs[idx], ys[idx]), xycoords='data',
                     xytext=xycoor[idx], textcoords='offset points', fontsize=10)
    plt.ylabel(u'True Positive Rate', fontdict=font)
    plt.xlabel(u'False Positive Rate', fontdict=font)
    plt.ylim((0, 1.0))
    plt.xlim(0, 1.0)
    _ticks = [0, ]
    _ticks.extend([i * 0.1 for i in range(1, 11)])
    plt.yticks(_ticks, ['{_y:.1f}'.format(_y=i) for i in _ticks], family='Times New Roman')
    _ticks= [i * 0.1 for i in range(1, 11)]
    plt.xticks(_ticks, ['{_x:.1f}'.format(_x=i) for i in _ticks], family='Times New Roman')
    # picname = 'LR-Better2-ROC'
    picname = 'Bayes-Better2-ROC'
    picname = 'SVM-Better2-ROC'
    plt.savefig('D://papers//Graduate//dataset//1//{picname}.svg'.format(picname=picname))
    plt.show()

def plotTogether(lr, bayes, svm):
    font = {'family': 'Times New Roman',
            'weight': 'normal',
            'size': 16,
            }
    plt.figure(figsize=(8, 6), dpi=80)
    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6))
    # LR
    xs = [0.2, 0.514]
    ys = [0.6, 0.8]
    perf = [0.7013, 0.7265]
    xycoor = [(+8, -4),(-30, +8)]
    plt.plot(lr['x'], lr['y'], linestyle='-', color='black', lw=1.5, label='LR')
    for idx in range(0, 2):
        markerline, stemlines, baseline = plt.stem([xs[idx], ], [ys[idx], ], linefmt='k-', markerfmt='ko', basefmt='-',
                                                   linewidth=1.2)
        plt.setp(stemlines, 'linewidth', 1.2)
        plt.plot([0, xs[idx]], [ys[idx], ys[idx]], color='black', linewidth=1.2, linestyle='-')
        plt.annotate(r'({_x:.3f}, {_y:.3f})'.format(_x=xs[idx], _y=ys[idx]),
                     xy=(xs[idx], ys[idx]), xycoords='data',
                     xytext=xycoor[idx], textcoords='offset points', fontsize=10)
    # Bayes
    xs = [0.2, 0.480]
    ys = [0.467, 0.8]
    perf = [0.7000, 0.7300]
    xycoor = [(+8, -4),(-77, +8)]
    plt.plot(bayes['x'], bayes['y'], linestyle=':', color='black', lw=1.5, label='Bayes')
    for idx in range(0, 2):
        markerline, stemlines, baseline = plt.stem([xs[idx], ], [ys[idx], ], linefmt='k:', markerfmt='k*', basefmt=':',
                                                   linewidth=1.2)
        plt.setp(stemlines, 'linewidth', 1.2)
        plt.plot([0, xs[idx]], [ys[idx], ys[idx]], color='black', linewidth=1.2, linestyle=':')
        plt.annotate(r'({_x:.3f}, {_y:.3f})'.format(_x=xs[idx], _y=ys[idx]),
                     xy=(xs[idx], ys[idx]), xycoords='data',
                     xytext=xycoor[idx], textcoords='offset points', fontsize=10)
    # SVM
    xs = [0.2, 0.5350]
    ys = [0.6042, 0.8]
    perf = [0.7000, 0.7300]
    xycoor = [(-75, +8), (+8, -10)]
    plt.plot(svm['x'], svm['y'], linestyle='--', color='black', lw=1.5, label='SVM')
    for idx in range(0, 2):
        markerline, stemlines, baseline = plt.stem([xs[idx], ], [ys[idx], ], linefmt='k--', markerfmt='kx', basefmt='--',
                                                   linewidth=1.2)
        plt.setp(stemlines, 'linewidth', 1.2)
        plt.plot([0, xs[idx]], [ys[idx], ys[idx]], color='black', linewidth=1.2, linestyle='--')
        plt.annotate(r'({_x:.3f}, {_y:.3f})'.format(_x=xs[idx], _y=ys[idx]),
                     xy=(xs[idx], ys[idx]), xycoords='data',
                     xytext=xycoor[idx], textcoords='offset points', fontsize=10)

    plt.ylabel(u'True Positive Rate', fontdict=font)
    plt.xlabel(u'False Positive Rate', fontdict=font)
    plt.ylim((0, 1.0))
    plt.xlim(0, 1.0)
    plt.legend(loc='lower right')
    _ticks = [0, ]
    _ticks.extend([i * 0.1 for i in range(1, 11)])
    plt.yticks(_ticks, ['{_y:.1f}'.format(_y=i) for i in _ticks], family='Times New Roman')
    _ticks = [i * 0.1 for i in range(1, 11)]
    plt.xticks(_ticks, ['{_x:.1f}'.format(_x=i) for i in _ticks], family='Times New Roman')
    # picname = 'LR-Better2-ROC'
    # picname = 'Bayes-Better2-ROC'
    # picname = 'SVM-Better2-ROC'
    picname = 'ROC-All'
    plt.savefig('D://papers//Graduate//dataset//1//{picname}.svg'.format(picname=picname))
    plt.show()
if __name__ == '__main__':
    proj_dir = '..'
    # base_dataset = loadData(proj_dir+'/data',  'SVM-better2.txt')
    # better_dataset = loadData(proj_dir+'/data', 'SVM-better2.txt')
    # # perfPlot(base_dataset, better_dataset)
    lr = loadData(proj_dir+'/data', 'LR-better2.txt')
    bayes = loadData(proj_dir+'/data', 'Bayes-better2.txt')
    svm = loadData(proj_dir+'/data', 'SVM-better2.txt')
    plotTogether(lr, bayes, svm)



