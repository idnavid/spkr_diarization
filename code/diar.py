import tools
import sad
import feat
import cluster
import bic

if __name__=='__main__':
    root_dir = './'
    out=tools.prepare_root(root_dir)
    wavname = tools.read_input()
    basename = tools.gen_uid(wavname)
    
    # SAD
    sadname = '%s/%s_sad.txt'%(out,basename)
    sad.run_sad(wavname,sadname)
    
    
    # MFCC
    featname = '%s/%s_feat.mfc'%(out,basename)
    feat.run_mfcc(wavname,featname)
    
    # BIC
    bicname = '%s/%s_bic.txt'%(out,basename)
    bic.run_bic(featname,sadname,bicname)
    
    # CLUSTERING
    clustname = '%s/%s_cluster.txt'%(out,basename)
    cluster.run_clustering(featname,bicname,clustname)

    
