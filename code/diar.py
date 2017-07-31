import tools
import sad
import feat
import cluster
import bic
import gmm
import resegment

if __name__=='__main__':
    root_dir = './'
    out=tools.prepare_root(root_dir)
    wavname,ubmname = tools.read_input()
    basename = tools.gen_uid(wavname)
    sadname = '%s/%s_sad.txt'%(out,basename)
    featname = '%s/%s_feat.mfc'%(out,basename)
    bicname = '%s/%s_bic.txt'%(out,basename)
    clustname = '%s/%s_cluster.txt'%(out,basename)
    viterbiname = '%s/%s_viterbi.txt'%(out,basename)
    attr = {'audio':wavname,
             'mfcc':featname,
             'sad':sadname,
             'bic':bicname,
             'cluster':clustname,
             'viterbi':viterbiname}

    # SAD
    sad.run_sad(attr)

    # MFCC
    feat.run_mfcc(attr)
    
    # BIC
    bic.run_bic(attr)
    
    # CLUSTERING
    cluster.run_clustering(attr)

    
    # Pick top clusters
    labels, segment_starts,segment_ends = tools.read_segs(attr['cluster'])
    top_n = tools.top_n_clustesr(labels, segment_starts,segment_ends,n=2)


    # Adapt UBM for each cluster.
    cluster_gmms = {}
    for i in top_n:
        cluster = 'C%s'%(str(i))
        gmmname = gmm.adapt(attr,cluster,ubmname)
        cluster_gmms[cluster] = gmmname

    # Resegmentation
    hmmname = '%s/%s_hmm.txt'%(out,basename)
    resegment.viterbi(attr,cluster_gmms,hmmname)
