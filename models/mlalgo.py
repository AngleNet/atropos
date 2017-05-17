"""
"""
import numpy as np
import codecs
from sklearn.linear_model import LogisticRegression
import sklearn.model_selection as ms
from sklearn import svm
from sklearn import naive_bayes
import sklearn.metrics as metrics
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('qt4agg')
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
plt.rcParams['axes.unicode_minus']=False

import pandas
import sys
sys.path.append('..')
import Spider.utils

def loadDataSet(fn):
    """
    Return an array of samples and their label.
    """
    labels = [k for k in Spider.utils.TrainningSample().__dict__.keys() if k != 'id']

    target_labels = ['pos',]
    feature_labels = [k for k in labels if k not in target_labels]

    __dataset = dict()
    for __label in feature_labels:
        __dataset[__label] = list()
    for __label in target_labels:
        __dataset[__label] = list()

    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            samp = Spider.utils.TrainningSample.lineSpliter(line)
            if samp:
                for __label in __dataset.keys():
                    __dataset[__label].append(getattr(samp, __label))
            else:
                Spider.utils.debug('Bypassing line: {line}'.format(line=line))
    return pandas.DataFrame(__dataset)

def autoNorm(dataSet, column):
    if column >= dataSet.shape[1]:
        debug("Wrong column number, could be too large.")
        import os; os.abort()
    _dataSet = dataSet[:, column]
    minVals = _dataSet.min(0)
    maxVals = _dataSet.max(0)
    ranges = maxVals - minVals
    norm = _dataSet - np.tile(minVals, _dataSet.shape[0])
    norm = norm / np.tile(ranges, _dataSet.shape[0])
    dataSet[:, column] = norm
    return dataSet


def runLR(dataset, target):
    model = LogisticRegression()
    runAndCheckCV(model, dataset, target, 'lr')

def runSVM(dataset, target):
    model = svm.SVC(kernel='linear', C=1)
    runAndCheckCV(model, dataset, target, 'svm')

def runBayes(dataset, target):
    model = naive_bayes.GaussianNB()
    runAndCheckCV(model, dataset, target, 'bayes')

def logToFile(fd, msg):
    if not fd:
        return
    fd.write(msg)


def runAndCheckCV(model, dataset, target, fname):
    scores = ms.cross_val_score(model, dataset, target, cv=10)
    with codecs.open(fname, 'w', 'utf-8') as fd:
        logToFile(fd, str(scores))
        logToFile(fd, "Accuracy: %0.4f (+/- %0.4f)\n" % (scores.mean(), scores.std() * 2))

def cvModels(dataset, target):
    runLR(dataset, target)
    runSVM(dataset, target)
    runBayes(dataset, target)

def evalRocCurve(dataset, target):
    random_state = np.random.RandomState(0)
    model = LogisticRegression()
    #model = svm.SVC(kernel='linear', random_state=random_state, probability=True)
    #model = naive_bayes.GaussianNB()
    fold = 0
    for train, test in ms.KFold(n_splits=5, shuffle=True,
                                random_state=random_state).split(dataset):
        fold += 1
        print("Running fold %d" % fold)
        train_dataset, train_target, test_dataset, test_target = \
            dataset[train], target[train], dataset[test], target[test]
        #model.classes_ gives the classes order
        prob = model.fit(train_dataset, train_target).predict_proba(test_dataset)
        fpr, tpr, shresholds = metrics.roc_curve(test_target, prob[:, 1])
        roc_auc = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=1.5, label='ROC fold %d (area = %0.2f)' % (fold, roc_auc))
    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Random')
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()

#Part I
#Precision, Recall, F1 score
def cacModelPrecision(dataset, target):
    rand = np.random.RandomState(0)
    model = LogisticRegression()
    #model = svm.SVC(kernel='linear', random_state=rand)
    #model = naive_bayes.GaussianNB()
    train_dataset, test_dataset, train_target, test_target= \
        ms.train_test_split(dataset, target, test_size=0.1, random_state=rand)
    target_pred = model.fit(train_dataset, train_target).predict(test_dataset)
    precision, recall, f1_score, support = metrics.precision_recall_fscore_support(
        test_target, target_pred, average='binary'
    )
    print(precision, recall, f1_score)

#Part II
def plotModelRoc(dataset, target):
    rand = np.random.RandomState(0)
    classifiers = {
        'LR': LogisticRegression(),
        'SVM':  svm.SVC(kernel='linear', random_state=rand, probability=True),
        'Bayes': naive_bayes.GaussianNB(),
    }
    train_dataset, test_dataset, train_target, test_target = \
        ms.train_test_split(dataset, target, test_size=0.1, random_state=rand)
    for cls_name, cls in classifiers.items():
        debug('Modeling %s' % cls_name)
        prob = cls.fit(train_dataset, train_target).predict_proba(test_dataset)
        fpr, tpr, shresholds = metrics.roc_curve(test_target, prob[:, 1])
        roc_auc = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=1.5, label='%s (area = %0.2f)' % (cls_name, roc_auc))
    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Random')
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()

def plotModelRoc2(dataset, target):
    rand = np.random.RandomState(0)
    classifiers = {
        'LR': LogisticRegression(),

        'SVM':  svm.SVC(kernel='linear', random_state=rand, probability=True),
        'Bayes': naive_bayes.GaussianNB(),
    }
    train_dataset, test_dataset, train_target, test_target = \
        ms.train_test_split(dataset, target, test_size=0.1, random_state=rand)
    for cls_name, cls in classifiers.items():
        debug('Modeling %s' % cls_name)
        prob = cls.fit(train_dataset, train_target).predict_proba(test_dataset)
        fpr, tpr, shresholds = metrics.roc_curve(test_target, prob[:, 1])
        roc_auc = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, ':',  lw=1.5, label='基准特征 %s (area = %0.2f)' % (cls_name, roc_auc))

    pos_data, pos_label = loadDataSet('../../Dataset/beta/samples.pos.new', 'pos', 4)
    __neg_data, __neg_label = loadDataSet('../../Dataset/beta/samples.neg.new', 'neg', 4)
    neg_data = np.random.permutation(__neg_data)
    neg_label = __neg_label[:pos_data.shape[0]]
    dataset = np.append(pos_data, neg_data[:pos_data.shape[0], :], axis=0)
    dataset = autoNorm(dataset, 0)
    dataset = autoNorm(dataset, 2)
    target = np.append(pos_label, neg_label)
    train_dataset, test_dataset, train_target, test_target = \
        ms.train_test_split(dataset, target, test_size=0.1, random_state=rand)
    for cls_name, cls in classifiers.items():
        debug('Modeling %s' % cls_name)
        prob = cls.fit(train_dataset, train_target).predict_proba(test_dataset)
        fpr, tpr, shresholds = metrics.roc_curve(test_target, prob[:, 1])
        roc_auc = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=1.5, label='基准特征+流行度 %s (area = %0.2f)' % (cls_name, roc_auc))

    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Random')
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()

#PartIII
def superParameterK(dataset, target):
    pass

if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]

    dataset = loadDataSet('{dir}/data/samples.train'.format(dir=proj_dir))
    neg_data = np.random.permutation(__neg_data)
    #neg_label = __neg_label[:pos_data.shape[0]]
    neg_label = __neg_label
    dataset = np.append(pos_data, neg_data, axis=0)
    dataset = autoNorm(dataset, 0)
    dataset = autoNorm(dataset, 2)
    target = np.append(pos_label, neg_label)

    #cvModels(dataset, target)
    #evalRocCurve(dataset, target)
    cacModelPrecision(dataset, target)
    #plotModelRoc(dataset, target)
    #plotModelRoc2(dataset, target)







