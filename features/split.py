import codecs
import Spider.utils
if __name__ == '__main__':
    proj = '..'
    res_dir = proj + '/result'
    data_dir = proj + '/data'
    samps = dict()
    with codecs.open('{dir}/samples.train'.format(dir=data_dir),'r','utf-8') as fd:
        for line in fd.readlines():
            samp = Spider.utils.TrainningSample.lineSpliter(line)
            if samp and samp.id not in samps:
                samps[samp.id] = samp
    with codecs.open('{dir}/samples.train.neg'.format(dir=res_dir), 'w', 'utf-8') as fd:
        for samp in samps.values():
            if samp.pos == 0:
                fd.write(str(samp) + '\n')
    with codecs.open('{dir}/samples.train.pos'.format(dir=res_dir), 'w', 'utf-8') as fd:
        for samp in samps.values():
            if samp.pos == 1:
                fd.write(str(samp) + '\n')
