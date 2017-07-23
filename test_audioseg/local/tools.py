# Script to interpret diarization results on a audio file. 
import numpy as np
from scipy.io import wavfile
import sys
#import pylab


def add_wgn(s,var=1e-4):
    """ Add white Gaussian noise to signal
        If no variance is given, simply add jitter. 
        This is for numerical stability purposes. """
    noise = np.random.normal(0,var,len(s))
    np.random.seed(0)
    return s + noise

def read_wav(filename):
    """
        read wav file. 
        Normalizes signal to values between -1 and 1. 
        Also add some jitter to remove all-zero segments."""
    fs, s = wavfile.read(filename) # scipy reads int
    s = np.array(s)/float(max(abs(s)))
    s = add_wgn(s) # Add jitter for numerical stability
    return fs,s

def time_to_sample(time_stamp,fs=16000.):
    """
       Convert time value in seconds to sample. """
    return 1 + int(time_stamp*fs)

def sample_to_frames(nsamples,fs=16000.,frame_shift=0.01):
    return int(nsamples/(frame_shift*fs))

def list_to_array(in_list):
    """
       Convert 1D list of numeric values to np array. 
       Added this because I had to use it several times. """
    out_array = np.array(in_list)
    return out_array.reshape((len(in_list),1))

def segs_to_stream(labels,segment_starts,segment_ends):
    """
       Compress labels, their start times, and their end times 
       into a single numpy array. This is for plotting purposes.
        """
    N = segment_ends[-1][0]
    stream = np.zeros((N,1))
    for i in range(labels.shape[0]):
        stream[segment_starts[i,0]:segment_ends[i,0]] = labels[i]
    return stream

def rm_empties(in_list):
    out_list = []
    for i in in_list:
        if i.strip()!='':
            out_list.append(i)
    return out_list

def read_segs(filename, fs=16000.0):
    """
        read segment file.
        Uses the segment file format defined by AudioSeg. 
        lines contain three fields:
        label start_time end_time
    """
    # For SAD segments, labels are limited ot sil and speech.
    # Other segments, use different label values. 
    # NOTE: will have to add conditions for cluster and bic segments. 
    fin = open(filename)
    labels = []
    segment_starts = []
    segment_ends = []
    for i in fin:
        line = i.strip()
        temp = line.split(' ')
        line_list = rm_empties(temp)
        if line_list[0]=='sil':
            labels.append(0)
        elif line_list[0]=='speech':
            labels.append(1)
        elif 'C' in line_list[0]:
            # For when reading cluster labels CX
            labels.append(int(line_list[0][1:]))
        segment_starts.append(time_to_sample(float(line_list[1].strip()),fs))
        segment_ends.append(time_to_sample(float(line_list[2].strip()),fs))
    fin.close()
    labels = list_to_array(labels)
    segment_starts = list_to_array(segment_starts)
    segment_ends = list_to_array(segment_ends)
    label_stream = segs_to_stream(labels,segment_starts,segment_ends)
    return label_stream, labels, segment_starts,segment_ends

def top_n_clustesr(labels, segment_starts,segment_ends,n=2):
    """ 
        Finds top n (typically 2) clusters in the segment file. 
        By top n we mean the n clusters with most cummulative segment length."""
    # Total number of clusters is largest cluster id +1 (to count silence)
    cluster_durations = np.zeros((np.max(labels)+1,1))
    for i in range(labels.shape[0]):
        cluster_durations[labels[i,0],0] += segment_ends[i,0] - segment_starts[i,0]
    # Multiply by -1, because argsort sorts in ascending order.
    sorted_clusters = np.argsort(-1*cluster_durations,axis=0)
    top_n = []
    i = 0
    while len(top_n) < n:
        # This if statement is to exclude silence (i.e., label = 0)
        if sorted_clusters[i,0]!=0:
            top_n.append(sorted_clusters[i,0])
        i += 1
    return top_n


def estimate_state_trans(top_n, labels,segment_starts,segment_ends):
    """
       n of the clusters are considered "states" for an HMM. This function 
      estimates a state transition matrix for these clusters. The matrix is 
      an nxn matrix of probabilities. The i-j element is the probability of the 
      i-th element of top_n transitioning to the j-th element of top_n. """
    
    # Because the values in top_n correspond to clusters
    # but values in trans_mat are from 1 to n. 
    idx_map = {}
    idx = 0
    for i in top_n:
        idx_map[i] = idx
        idx+=1

    trans_mat=np.zeros((len(top_n),len(top_n)))
    prev_state = 0
    for i in range(labels.shape[0]):
        this_state = labels[i,0]
        if (this_state in top_n) and (prev_state in top_n):
            trans_mat[idx_map[prev_state],idx_map[this_state]] += 1.e5
        if this_state in top_n:
            T = time_to_sample(segment_ends[i,0]-segment_starts[i,0])
            n_frames = sample_to_frames(T)
            trans_mat[idx_map[this_state],idx_map[this_state]] += n_frames
            prev_state = this_state
    trans_mat = 1.*trans_mat
    row_sum = trans_mat.sum(axis=1)
    row_sum = row_sum.T
    print trans_mat/row_sum.reshape(1,len(top_n))

if __name__=='__main__':
    #fname='/Users/navidshokouhi/Downloads/unimaquarie/projects/ami_sample/amicorpus/ES2002a/audio/ES2002a.Mix-Headset.wav'
    #fs,s = read_wav(fname)
    fs = 16000.
    #segname='/home/navid/spkr_diarization/test_audioseg/out_dir/ES2002a.clusters'
    segname = sys.argv[1]
    # 1. Plot labels
    #labels,a,b,c = read_segs(segname,fs)
    #pylab.plot(s)
    #pylab.plot(labels/40.)
    #pylab.show()
    #print len(labels)
    
    # 2. Find top clusters
    a, labels, segment_starts,segment_ends = read_segs(segname,fs)
    top_clusters=top_n_clustesr(labels, segment_starts,segment_ends,n=4)
    for i in top_clusters:
        print i
    estimate_state_trans(top_clusters, labels,segment_starts,segment_ends)
