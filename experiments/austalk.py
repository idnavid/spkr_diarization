import tools
import sad
import feat
import cluster
import bic
import gmm
import resegment

root_dir = './'
out=tools.prepare_root(root_dir)
wavname,_ = tools.read_input()
basename = tools.gen_uid(wavname)
sadname = '%s/%s_sad.txt'%(out,basename)
featname = '%s/%s_feat.mfc'%(out,basename)
bicname = '%s/%s_bic.txt'%(out,basename)
clustname = '%s/%s_cluster.txt'%(out,basename)
attr = {'audio':wavname,
        'mfcc':featname,
        'sad':sadname,
        'bic':bicname,
        'cluster':clustname}
