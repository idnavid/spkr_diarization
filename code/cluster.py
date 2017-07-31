import os
import tools
import sad
import feat
import bic

def run_clustering(attr):
    featname = attr['mfcc']
    bicname = attr['bic']
    clustname = attr['cluster']
    path = tools.set_path()
    command = '%s/scluster -i -n 2 --label=unk %s %s %s'
    exe_cmd = command%(path['audioseg'],featname,bicname,clustname)
    os.system(exe_cmd)
    return


if __name__=='__main__':
    wavname = '/Users/navidshokouhi/Downloads/unimaquarie/projects/ami_sample/amicorpus/ES2002a/audio/ES2002a.Mix-Headset.wav'
    basename = tools.gen_uid(wavname)
    sadname = './%s_sad.txt'%(basename)
    featname = './%s.mfc'%(basename)
    bicname = './%s_bic.txt'%(basename)
    clustname = './%s_cluster.txt'%(basename)
    attr = {'audio':wavname,
            'mfcc':featname,
            'bic':bicname,
            'sad':sadname,
            'cluster':clustname}
    
    sad.run_sad(attr)
    feat.run_mfcc(attr)
    bic.run_bic(attr)
    run_clustering(attr)

