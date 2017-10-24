import sys
sys.path.append('../code/')

import tools
import sad
import feat
import cluster
import bic

root_dir = './'
out=tools.prepare_root(root_dir)
wavname,_ = tools.read_input()
basename = tools.gen_uid(wavname)
attr = tools.gen_attr(out,basename,wavname)

sad.run_sad(attr)
feat.run_mfcc(attr)
bic.run_bic(attr,'uniform')
cluster.run_clustering(attr)


