
import codecs, Spider.utils

if __name__ == '__main__':
    proj_dir = '..'
    res_dir = proj_dir + '/result'
    data_dir = proj_dir + '/data'
    samps = dict()
    with codecs.open(data_dir + '/samples.train', 'r', 'utf-8') as fd:
        for line in fd.readlines():
            samp = Spider.utils.TrainningSample.lineSpliter(line)
            if samp and samp.id not in samps:
                samps[samp.id] = samp

    with codecs.open(res_dir + '/samples.train','w','utf-8') as fd:
        for samp in samps.values():
            if samp.trending_index > 0.05:
                continue
            fd.write(str(samp) + '\n')