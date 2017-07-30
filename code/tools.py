import os
import sys
import uuid
import numpy as np


# DISK I/O functions
def prepare_root(root_dir):
    out='%s/out_dir/'%(root_dir)
    command = 'mkdir -p %s'
    exe_cmd = command%(out)
    os.system(exe_cmd)
    return out


def read_input():
    wavname = sys.argv[1]
    return wavname

def set_path():
    spro_path='/Users/navidshokouhi/Software_dir/audioseg_dir/spro-5.0/'
#    spro_path='/home/navid/tools/spro-4.0/'
    audioseg_path ='/Users/navidshokouhi/Software_dir/audioseg_dir/audioseg-1.1/src/'
#    audioseg_path='/home/navid/tools/audioseg-1.1/src/'
    return {'spro':spro_path,'audioseg':audioseg_path}

def gen_uid(wavname):
    """
    Generate unique id based on input wavname.
    """
    basename = wavname.split('/')[-1]
    basename = basename[:-4] # Do not include .wav extention
    basename = '%s_%s'%(basename,str(uuid.uuid4().fields[-1])[:5])
    return basename


def time_to_sample(time_stamp,fs=16000.):
    """
        Convert time value in seconds to sample. """
    return 1 + int(time_stamp*fs)

def list_to_array(in_list):
    """
        Convert 1D list of numeric values to np array.
        Added this because I had to use it several times. """
    out_array = np.array(in_list)
    return out_array.reshape((len(in_list),1))

def rm_empties(in_list):
    """
    remove empty characters from list. 
    We need this because audioseg doesn't 
    use single-space for delimeters. 
    """
    out_list = []
    for i in in_list:
        if i.strip()!='':
            out_list.append(i)
    return out_list


def read_segs(segname, fs=16000.0):
    """
        read segment file.
        Uses the segment file format defined by AudioSeg.
        lines contain three fields:
        label start_time end_time
        """
    # For SAD segments, labels are limited ot sil and speech.
    # Other segment types use different label values.
    fin = open(segname)
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
    return labels, segment_starts,segment_ends

def top_n_clustesr(labels, segment_starts,segment_ends,n=2):
    """
        Finds top n (typically 2) clusters in the segment file.
        By top n we mean the n clusters with most cummulative segment length.
        """
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
