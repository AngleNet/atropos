import codecs
import sys
sys.path.append('..')
import Spider.utils

def sampleSize(samples):
    pos = 0
    neg = 0
    for samp in samples.values():
        if samp.truly_retweeted == '0':
            neg += 1
        else:
            pos += 1
    return (pos, neg)
if __name__ == '__main__':
    if len(sys.argv) == 1:
        proj_dir = '../'
    else:
        proj_dir = sys.argv[1]
    samps = dict()
    with codecs.open('{proj_dir}result/tweets.sample'.format(proj_dir=proj_dir),
                     'r', 'utf-8') as fd:
        for line in fd.readlines():
            samp = Spider.utils.weiboSampleLineSpliter(line)
            if samp and samp.id not in samps:
                samps[samp.id] = samp
    with codecs.open('{proj_dir}result/tweets.sample'.format(proj_dir=proj_dir),
                     'w', 'utf-8') as fd:
        for samp in samps.values():
            fd.write(str(samp) + '\n')
    num_pos, num_neg = sampleSize(samps)
    print('********Samples Statistics********')
    print('Postive samples: {pos}, Negative samples: {neg}'.format(pos=num_pos, neg=num_neg))
