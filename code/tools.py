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
    ubmname = sys.argv[2]
    return wavname,ubmname

def set_path():
    spro_path='/Users/navidshokouhi/Software_dir/audioseg_dir/spro-5.0/'
    #spro_path='/home/navid/tools/spro-4.0/'
    audioseg_path ='/Users/navidshokouhi/Software_dir/audioseg_dir/audioseg-1.1/src/'
    #audioseg_path='/home/navid/tools/audioseg-1.1/src/'
    return {'spro':spro_path,'audioseg':audioseg_path}

def gen_uid(wavname):
    """
    Generate unique id based on input wavname.
    """
    basename = wavname.split('/')[-1]
    basename = basename[:-4] # Do not include .wav extention
    basename = '%s_%s'%(basename,str(uuid.uuid4().fields[-1])[:5])
    return basename


# Reading Segments
def time_to_sample(time_stamp,fs=16000.):
    """
        Convert time value in seconds to sample. """
    return 1 + int(time_stamp*fs)

def sample_to_time(sample,fs=16000.):
    """
        Convert time value in seconds to sample. """
    return sample/fs

def list_to_array(in_list):
    """
        Convert 1D list of numeric values to np array.
        Added this because I had to use it several times. 
    """
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

def write_segs(labels,segment_starts,segment_ends,segname):
    N = labels.shape[0]
    fout = open(segname,'w')
    line = '%s %.2f %.2f\n'
    for i in range(N):
        seg = line%(str(int(labels[i,0])),(segment_starts[i,0]),(segment_ends[i,0]))
        fout.write(seg)
    fout.close()

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
        else:
            # Assumes labels are digits
            labels.append(int(line_list[0]))
        segment_starts.append(time_to_sample(float(line_list[1].strip()),fs))
        segment_ends.append(time_to_sample(float(line_list[2].strip()),fs))
    fin.close()
    labels = list_to_array(labels)
    segment_starts = list_to_array(segment_starts)
    segment_ends = list_to_array(segment_ends)
    return labels, segment_starts,segment_ends


def segs_to_stream(labels,segment_starts,segment_ends):
    """
    Compress labels, their start times, and their end times
    into a single numpy array. This is for plotting purposes.
    """
    N = segment_ends[-1][0]
    stream = np.zeros((N,1))
    for i in range(labels.shape[0]):
        stream[segment_starts[i,0]:segment_ends[i,0],0] = labels[i][0]
    return stream


def merge_segs(segname1,segname2):
    labels1, segment_starts1,segment_ends1 = read_segs(segname1)
    label_stream1 = segs_to_stream(labels1,segment_starts1,segment_ends1)
    labels2, segment_starts2,segment_ends2 = read_segs(segname2)
    label_stream2 = segs_to_stream(labels2,segment_starts2,segment_ends2)

    label_stream1 = np.multiply(label_stream2,label_stream1)
    breaks = np.diff(label_stream1,axis=0)
    labels = []
    segment_starts = []
    segment_ends = []
    start = 0.
    for i in range(1,breaks.shape[0]):
        if breaks[i,0] != 0:
            end = sample_to_time(i)
            labels.append(label_stream1[i-1,0])
            segment_starts.append(start)
            segment_ends.append(end)
            start = sample_to_time(i+1)
    return list_to_array(labels),list_to_array(segment_starts),list_to_array(segment_ends)



def read_annotations(filename):
    """
    Reads dolby annotations. 
    segment start/ends are originally in 10ms frames. 
    *dt in the transcription indicates secondary speaker.
    """
    fin = open(filename)
    labels = []
    segment_starts = []
    segment_ends = []
    for i in fin:
        line_list = i.strip().split('\t')
        line_fields = rm_empties(line_list)
        if '*dt' in line_fields[3]:
            labels.append(2)
        else:
            labels.append(1)
        segment_starts.append(time_to_sample(int(line_fields[0])*0.01))
        segment_ends.append(time_to_sample(int(line_fields[1])*0.01))
    labels = list_to_array(labels)
    segment_starts = list_to_array(segment_starts)
    segment_ends = list_to_array(segment_ends)
    return labels,segment_starts,segment_ends


# Clustering functions
def top_n_clusters(labels, segment_starts,segment_ends,n=2):
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



if __name__=='__main__':
    filename = '/Users/navidshokouhi/Downloads/unimaquarie/projects/dolby-annotations/out/1_222_2_7_001-ch6-speaker16.out'
    labels, seg_starts, seg_ends = read_annotations(filename)
    stream = segs_to_stream(labels,seg_starts,seg_ends)
    import pylab
    pylab.plot(stream)
    filename = 'out_dir/final_diar.txt'
    labels, seg_starts, seg_ends = read_segs(filename)
    stream= segs_to_stream(labels,seg_starts,seg_ends)
    pylab.plot(stream)
    pylab.show()
