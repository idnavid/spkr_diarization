import numpy as np
import tools
import os
import tools
import sad
import feat
import bic
import cluster

def print_hmm_trans(cluster_dict,trans_mat,hmmname):
    fout = open(hmmname,'w')
    n = len(cluster_dict)
    fout.write(str(n)+'\n')
    for i in cluster_dict:
        line = '%s %s\n'%(i,cluster_dict[i])
        fout.write(line)
    # Eneter/Exit Probabilities are determined
    # by the number of clusters.
    enter_probs = np.ones((1,n))*1.0
    enter_probs = enter_probs/n
    exit_probs = enter_probs
    for i in range(n):
        if i < n - 1:
            fout.write(str(enter_probs[0,i])+' ')
        else:
            fout.write(str(enter_probs[0,i])+'\n')

    for i in range(n):
        for j in range(n):
            if j < n-1:
                fout.write(str(trans_mat[i,j])+' ')
            else:
                fout.write(str(trans_mat[i,j])+'\n')
    for i in range(n):
        if i < n - 1:
            fout.write(str(exit_probs[0,i])+' ')
        else:
            fout.write(str(exit_probs[0,i])+' ')
    fout.close()
    return

def state_transitions(cluster_dict,segname,hmmname):
    """
    Build state transition matrix using a subset of 
    the clusters in clusterlist. 
    Transitions are empirically estimtated from the 
    segment file, segname. Segname is typically the 
    output of the clustering module.
    
    returns the file hmmname, which points to the 
    location of the state transition text file.
    """
    
    # The following loop serves two purposes:
    # 1. it gives us cluster ids, which are the
    # integer labels of the clusters, say 20 in C20.
    # This becomes useful in checking the states.
    # 2. it creates idx_map, which is a mapping from
    # values between 0 to n-1 for the n clusters.
    n = len(cluster_dict)
    idx_map = {}
    idx = 0
    cluster_ids = []
    for i in cluster_dict:
        cluster = i
        idx_map[int(i[1:])] = idx
        cluster_ids.append(int(i[1:]))
        idx+=1
    
    
    
    trans_mat=np.zeros((n,n))
    labels, segment_starts,segment_ends = tools.read_segs(segname)
    # First estimate diagonal elements.
    prev_state = 0
    for i in range(labels.shape[0]):
        this_state = labels[i,0]
        if (this_state in cluster_ids) and (prev_state == this_state):
            trans_mat[idx_map[this_state],idx_map[this_state]] += 1.
        if this_state in cluster_ids:
            prev_state = this_state
    N = trans_mat.sum()
    trans_mat = trans_mat/float(N)
    print trans_mat
    # Estimate off-diagonal elements using
    # equation (5) from Meignier et al. 2017, "Step-by-step and
    # integrated approaches in broadcast news speakerdiarization".
    for i in range(trans_mat.shape[0]):
        pii = trans_mat[i,i]
        pij = (1 - pii)/(n-1)
        for j in range(trans_mat.shape[1]):
            if i!=j:
                trans_mat[i,j] = pij
    print_hmm_trans(cluster_dict,trans_mat,hmmname)
    return



def viterbi(attr,cluster_dict,hmmname):
    featname = attr['mfcc']
    viterbiname = attr['viterbi']
    segname = attr['cluster']
    state_transitions(cluster_dict,segname,hmmname)
    path = tools.set_path()
    command = '%s/sviterbi %s %s %s'
    exe_cmd = command%(path['audioseg'],hmmname,featname,viterbiname)
    os.system(exe_cmd)
    return



if __name__=='__main__':
    wavname = '/Users/navidshokouhi/Downloads/unimaquarie/projects/ami_sample/amicorpus/ES2002a/audio/ES2002a.Mix-Headset.wav'
    basename = tools.gen_uid(wavname)
    sadname = './%s_sad.txt'%(basename)
    featname = './%s.mfc'%(basename)
    bicname = './%s_bic.txt'%(basename)
    clustname = './%s_cluster.txt'%(basename)
    hmmname = './%s_hmm.mdl'%(basename)
    
    attr = {'audio':wavname,
        'mfcc':featname,
        'sad':sadname,
        'bic':bicname,
        'cluster':clustname}

    sad.run_sad(attr)
    feat.run_mfcc(attr)
    bic.run_bic(attr)
    cluster.run_clustering(attr)
    
    # Pick top clusters
    labels, segment_starts,segment_ends = tools.read_segs(clustname)
    top_n = tools.top_n_clustesr(labels, segment_starts,segment_ends)
    
    cluster_dict = {}
    for i in top_n:
        cluster = 'C%s'%(str(i))
        gmmname = 'tmp_name'
        cluster_dict[cluster] = gmmname

    state_transitions(cluster_dict,clustname,hmmname)
    



    
