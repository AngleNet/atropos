import codecs, sys
sys.path.append('..')
import Spider.utils

def loadSample(fn):
    samps = dict()
    with codecs.open(fn, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            samp = Spider.utils.sampleLineSpliter(line)
            if samp and samp.id not in samps:
                samps[samp.id] = samp
    return samps

if __name__ == '__main__':
    if len(sys.argv) < 2:
        proj_dir = '..'
    else:
        proj_dir = sys.argv[1]
    data_dir = proj_dir + '/data'
    res_dir = proj_dir + '/result'

    trdx_samps = loadSample(data_dir + '/sample')
    users = Spider.utils.loadUsers(data_dir + '/users')
    samps = dict()

    user_extras = dict()
    for samp in trdx_samps.values():



