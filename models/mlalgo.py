"""
"""
import numpy as np
import codecs, sklearn,os
from sklearn.linear_model import LogisticRegressionCV, LogisticRegression
import sklearn.model_selection as ms
from sklearn import svm
from sklearn import naive_bayes
from sklearn import tree
import sklearn.metrics as metrics
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('qt4agg')
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
plt.rcParams['axes.unicode_minus']=False

import pandas
import sys, glob
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
    _dataset = pandas.DataFrame(__dataset)
    num_pos = len(_dataset[_dataset['pos']==1])
    _dataset_pos = _dataset[_dataset['pos']==1]
    _dataset.drop(_dataset['pos']==1,inplace=1,axis=0)
    _dataset_neg = _dataset[:num_pos]
    new_dataset = _dataset_pos.append(_dataset_neg)
    return new_dataset
    # print (new_dataset.shape,num_pos)
    # print (_dataset.shape)

def checkDataSet(dataset):
    pass

def preprocessing(dataset):
    dataset = dataset.sample(n=dataset.shape[0])
    _labels = ['num_followers', 'num_urls', 'content_len']
    min_max_scaler = sklearn.preprocessing.MinMaxScaler()
    for _label in _labels:
        dataset[_label] = min_max_scaler.fit_transform(dataset[_label].values.reshape(-1,1))
    dataset['has_trending_topics']  /= 10
    dataset['num_trending_topics'] /= 10
    dataset['trending_index'] *= 25
    return dataset

def runLR(dataset, target, res_dir):
    model = LogisticRegression()
    runAndCheckCV(model, dataset, target, res_dir + '/lr')

def runSVM(dataset, target, res_dir):
    model = svm.SVC(kernel='linear', C=1)
    runAndCheckCV(model, dataset, target, res_dir + '/svm')

def runBayes(dataset, target, res_dir):
    model = naive_bayes.GaussianNB()
    runAndCheckCV(model, dataset, target, res_dir + '/bayes')

def logToFile(fd, msg):
    if not fd:
        return
    fd.write(msg)


def runAndCheckCV(model, dataset, target, fname):
    Spider.utils.debug('Modeling {model}'.format(model=str(model.__class__)))
    scores = ms.cross_val_score(model, dataset.values, target.values, cv=10)
    with codecs.open(fname, 'w', 'utf-8') as fd:
        logToFile(fd, str(list(scores)) + '\n')
        logToFile(fd, "Accuracy: %0.4f (+/- %0.4f)\n" % (scores.mean(), scores.std() * 2))
    Spider.utils.debug("Accuracy: %0.4f (+/- %0.4f)\n" % (scores.mean(), scores.std() * 2))

def cvModels(dataset, target, res_dir):
    runLR(dataset, target, res_dir)
    runSVM(dataset, target, res_dir)
    runBayes(dataset, target, res_dir)

def evalRocCurve(features, target):
    random_state = np.random.RandomState(0)
    model = LogisticRegression()
    #model = svm.SVC(kernel='linear', random_state=random_state, probability=True)
    #model = naive_bayes.GaussianNB()
    fold = 0
    for train, test in ms.KFold(n_splits=5, shuffle=True,
                                random_state=random_state).split(features):
        fold += 1
        print("Running fold %d" % fold)
        train_dataset, train_target, test_dataset, test_target = \
            features.values[train], target.values[train], features.values[test], target.values[test]
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
def cacModelPrecision(features, target, model='lr'):
    rand = np.random.RandomState(0)
    if model == 'lr':
        model = LogisticRegression(class_weight='balanced')
        Spider.utils.debug('Running LR')
    elif model == 'svm':
        model = svm.SVC(kernel='poly', random_state=rand, probability=True)
        Spider.utils.debug('Running SVM')
    elif model == 'bayes':
        model = naive_bayes.GaussianNB()
        Spider.utils.debug('Running Bayes')
    else:
        Spider.utils.debug('Bad model {model}'.format(model=model))
        return
    train_dataset, test_dataset, train_target, test_target= \
        ms.train_test_split(features, target, test_size=0.2, random_state=rand)
    # Plot Precision-Recall
    # prob = model.fit(train_dataset, train_target).predict_proba(test_dataset)
    # precision, recall, _ = metrics.precision_recall_curve(np.array(test_target), prob[:, 1])
    # plt.figure()
    # plt.plot(recall, precision, color='navy')
    # plt.show()

    target_pred = model.fit(train_dataset, train_target).predict(test_dataset)
    accu = metrics.accuracy_score(np.array(test_target), np.array(target_pred))

    precision = metrics.precision_score(np.array(test_target), np.array(target_pred))
    recall = metrics.recall_score(np.array(test_target), np.array(target_pred))
    f1_score = metrics.f1_score(np.array(test_target), np.array(target_pred))

    # Spider.utils.debug('Precision: {prec}%, Recall: {recall}%, F1: {fscore}%'.format(
    Spider.utils.debug('{prec:.2f}%, {recall:.2f}%, {fscore:.2f}%'.format(
        prec=precision*100,
        recall=recall*100,
        fscore=f1_score*100,
    ))

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
        Spider.utils.debug('Modeling %s' % cls_name)
        prob = cls.fit(train_dataset, train_target).predict_proba(test_dataset)
        fpr, tpr, shresholds = metrics.roc_curve(test_target, prob[:, 1])
        roc_auc = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=1.5, label='%s (area = %0.2f)' % (cls_name, roc_auc))
    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Random')
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('')
    plt.legend(loc="lower right")
    plt.show()

def plotModelRoc2(dataset, feature_cases):
    # Case: base
    features = dataset.filter(items=feature_cases['base'])
    rand = np.random.RandomState(0)
    classifiers = {
        'LR': LogisticRegression(class_weight='balanced'),
        #'SVM':  svm.SVC(kernel='poly', random_state=rand, probability=True),
        # 'Bayes': naive_bayes.GaussianNB(),
        # 'C4.5': tree.DecisionTreeClassifier(criterion='entropy')
    }
    train_dataset, test_dataset, train_target, test_target = \
        ms.train_test_split(features, target, test_size=0.1, random_state=rand)
    for cls_name, cls in classifiers.items():
        Spider.utils.debug('Modeling %s' % cls_name)
        _model = cls.fit(train_dataset, train_target)
        target_pred = _model.predict(test_dataset)

        precision = metrics.precision_score(np.array(test_target), np.array(target_pred))
        recall = metrics.recall_score(np.array(test_target), np.array(target_pred))
        f1_score = metrics.f1_score(np.array(test_target), np.array(target_pred))

        Spider.utils.debug('{prec:.2f}%, {recall:.2f}%, {fscore:.2f}%'.format(
            prec=precision * 100,
            recall=recall * 100,
            fscore=f1_score * 100,
        ))

        prob = _model.predict_proba(test_dataset)
        fpr, tpr, shresholds = metrics.roc_curve(test_target, prob[:, 1])
        roc_auc = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, ':',  lw=1.5, label='基准特征 %s (area = %0.2f)' % (cls_name, roc_auc))

    # Case: better3
    #       base + trending_index
    features = dataset.filter(items=feature_cases['better3'])
    train_dataset, test_dataset, train_target, test_target = \
        ms.train_test_split(features, target, test_size=0.1, random_state=rand)
    for cls_name, cls in classifiers.items():
        Spider.utils.debug('Modeling %s' % cls_name)
        _model = cls.fit(train_dataset, train_target)
        prob = _model.predict_proba(test_dataset)
        target_pred = _model.predict(test_dataset)

        precision = metrics.precision_score(np.array(test_target), np.array(target_pred))
        recall = metrics.recall_score(np.array(test_target), np.array(target_pred))
        f1_score = metrics.f1_score(np.array(test_target), np.array(target_pred))

        Spider.utils.debug('{prec:.2f}%, {recall:.2f}%, {fscore:.2f}%'.format(
            prec=precision * 100,
            recall=recall * 100,
            fscore=f1_score * 100,
        ))
        fpr, tpr, shresholds = metrics.roc_curve(test_target, prob[:, 1])
        roc_auc = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=1.5, label='基准特征+流行度 %s (area = %0.2f)' % (cls_name, roc_auc))

    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Random')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC 曲线')
    plt.legend(loc="lower right")
    plt.show()

def plotSingleModelRoc(dataset, feature_cases, model_name, feature_groups):
    groups = dict(base='基准特征', better1='基准特征+包含话题个数',
                  better2='基准特征+话题热度')
    rand = np.random.RandomState(0)
    classifiers = {
        'LR': LogisticRegression(class_weight='balanced'),
        'SVM':  svm.SVC(kernel='poly', random_state=rand, probability=True),
        'Bayes': naive_bayes.GaussianNB(),
         'C4.5': tree.DecisionTreeClassifier(criterion='entropy')
    }
    if model_name not in classifiers:
        Spider.utils.debug('Model name {name}s is not supported, only supports {models}s'.format(
            name=model_name, models=classifiers.keys()
        ))
        return
    model = classifiers[model_name]
    for case in feature_groups:
        train_dataset, test_dataset, train_target, test_target = \
            ms.train_test_split(dataset.filter(items=feature_cases[case]), dataset['pos'], test_size=0.1, random_state=rand)
        Spider.utils.debug('Modeling %s with %s ' % (model_name, groups[case]))
        _model = model.fit(train_dataset, train_target)
        target_pred = _model.predict(test_dataset)

        precision = metrics.precision_score(np.array(test_target), np.array(target_pred))
        recall = metrics.recall_score(np.array(test_target), np.array(target_pred))
        f1_score = metrics.f1_score(np.array(test_target), np.array(target_pred))

        Spider.utils.debug('{prec:.2f}%, {recall:.2f}%, {fscore:.2f}%'.format(
            prec=precision * 100,
            recall=recall * 100,
            fscore=f1_score * 100,
        ))

        prob = _model.predict_proba(test_dataset)
        fpr, tpr, shresholds = metrics.roc_curve(test_target, prob[:, 1])
        roc_auc = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=1.5, label='%s %s (area = %0.2f)' % (groups[case], model_name, roc_auc))

    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Random')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC 曲线')
    plt.legend(loc="lower right")
    plt.show()
#PartIII
def superParameterK(proj_dir, feature_cases, model_name, feature_group):
    groups = dict(base='基准特征', better1='基准特征+包含话题个数',
             better2 = '基准特征+话题热度')
    rand = np.random.RandomState(0)
    classifiers = {
        'LR': LogisticRegression(class_weight='balanced'),
        'SVM': svm.SVC(kernel='poly', random_state=rand, probability=True),
        'Bayes': naive_bayes.GaussianNB(),
        'C4.5': tree.DecisionTreeClassifier(criterion='entropy')
    }
    if model_name not in classifiers:
        Spider.utils.debug('Model name {name}s is not supported, only supports {models}s'.format(
            name=model_name, models=classifiers.keys()
        ))
        return
    model = classifiers[model_name]
    data_dir = proj_dir  + '/data'
    dataset_fs = glob.glob('{dir}/samples.train.*'.format(dir=data_dir))
    for _fname in sorted(dataset_fs, key=lambda x: int(x.split('.')[-1])):
        _num = os.path.basename(_fname).split('.')[-1]
        dataset = loadDataSet(_fname)
        train_dataset, test_dataset, train_target, test_target = \
            ms.train_test_split(dataset.filter(items=feature_cases[feature_group]), dataset['pos'], test_size=0.1,
                                random_state=rand)
        Spider.utils.debug('Modeling %s with %s (k=%s)' % (model_name, groups[feature_group], _num))
        _model = model.fit(train_dataset, train_target)
        target_pred = _model.predict(test_dataset)

        precision = metrics.precision_score(np.array(test_target), np.array(target_pred))
        recall = metrics.recall_score(np.array(test_target), np.array(target_pred))
        f1_score = metrics.f1_score(np.array(test_target), np.array(target_pred))
        Spider.utils.debug('{prec:.2f}%, {recall:.2f}%, {fscore:.2f}%'.format(
            prec=precision * 100,
            recall=recall * 100,
            fscore=f1_score * 100,
        ))
        prob = _model.predict_proba(test_dataset)
        fpr, tpr, shresholds = metrics.roc_curve(test_target, prob[:, 1])
        roc_auc = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=1.5, label='(k=%s) %s %s (area = %0.2f)' %
                                         (_num, groups[feature_group], model_name, roc_auc))
    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Random')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC 曲线')
    plt.legend(loc="lower right")
    plt.show()
    os.abort()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    _base_features = ['certified', 'num_followers', 'num_urls', 'num_videos',
                      'content_len', 'similarity']
    feature_cases = {
        'base': _base_features + ['has_trending_topics'],
        'better1': _base_features + ['num_trending_topics'],
        'better2': _base_features + ['trending_index'],
    }
    # superParameterK(proj_dir, feature_cases, 'Bayes', 'base')
    res_dir = proj_dir + '/result'
    dataset = loadDataSet('{dir}/data/samples.train'.format(dir=proj_dir))
    dataset = preprocessing(dataset)

    target = dataset['pos']
    features = dataset.filter(items=feature_cases['better2'])
    #cvModels(features, target, res_dir)
    #evalRocCurve(features, target)
    # cacModelPrecision(features, target, 'lr')
    # plotModelRoc(features, target)
    # plotModelRoc2(dataset, feature_cases)
    plotSingleModelRoc(dataset, feature_cases, 'LR', ['base', 'better1', 'better2'])
