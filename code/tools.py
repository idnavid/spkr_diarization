import os
import sys
import uuid
import numpy as np


# DISK I/O functions
#---------------------------------
def prepare_root(root_dir):
    """
    Prepares directory to store intermediate
    files onto disk.
    """
    rand_extention = str(uuid.uuid4().fields[-1])[:5]
    out='%s/out_%s/'%(root_dir,rand_extention)
    command = 'mkdir -p %s'
    exe_cmd = command%(out)
    os.system(exe_cmd)
    return out

#---------------------------------
def read_input():
    """
    Parses command line input. 
    This isn't a great way to write this, but
    it makes the main script look clean.
    """
    wavname = sys.argv[1]
    if wavname[-4:]!='.wav':
        raise ValueError('incorrect input wave format!')
    ubmname = sys.argv[2]
    return wavname,ubmname

#---------------------------------
def set_path():
    """
    specifies location of extra tools. 
    NOTE: This isn't a great way to write this, but it's
    useful because it summarizes all external packages here. 
    """
    spro_path='/Users/navidshokouhi/Software_dir/audioseg_dir/spro-5.0/'
    #spro_path='/home/navid/tools/spro-4.0/'
    audioseg_path ='/Users/navidshokouhi/Software_dir/audioseg_dir/audioseg-1.1/src/'
    #audioseg_path='/home/navid/tools/audioseg-1.1/src/'
    return {'spro':spro_path,'audioseg':audioseg_path}

#---------------------------------
def gen_uid(wavname):
    """
    Generate unique id based on input wavname.
    """
    basename = wavname.split('/')[-1]
    basename = basename[:-4] # Do not include .wav extention
    basename = '%s_%s'%(basename,str(uuid.uuid4().fields[-1])[:5])
    return basename


#---------------------------------
def gen_attr(out,basename,wavname):
    """
    Generate an attribute dictionary that contains
    the file names corresponding to all components: 
        sad
        features
        bic
        cluster
        viterbi
    """
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
    return attr

# Reading Segments
#---------------------------------
def time_to_sample(time_stamp,fs=16000.):
    """
        Convert time value in seconds to sample. """
    return 1 + int(time_stamp*fs)


#---------------------------------
def sample_to_time(sample,fs=16000.):
    """
        Convert time value in seconds to sample. """
    return sample/fs

#---------------------------------
def list_to_array(in_list):
    """
        Convert 1D list of numeric values to np array.
        Added this because I had to use it several times. 
    """
    out_array = np.array(in_list)
    return out_array.reshape((len(in_list),1))

#---------------------------------
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

#---------------------------------
def write_segs(labels,segment_starts,segment_ends,segname,fs=16000.,mode=''):
    print mode
    N = labels.shape[0]
    fout = open(segname,'w')
    line = '%s %.2f %.2f\n'
    for i in range(N):
        if labels[i,0] == 0:
            lab = 'sil'
        else:
            lab = str(int(labels[i,0]))
            if mode=='uniform':
                lab = 'unk'
        seg = line%(lab,(segment_starts[i,0]/fs),(segment_ends[i,0]/fs))
        fout.write(seg)
    fout.close()

#---------------------------------
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

#---------------------------------
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

#---------------------------------
def merge_segs(segname,sadname):
    """
        Merge speaker labels from segname with 
        sad labels. This function zeros out the segments 
        that have previously been labeled as silence.
    """
    return

#---------------------------------
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
#---------------------------------
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
    filename = 'out_dir/1_222_2_7_001-ch6-speaker16_18474_cluster.txt'
    labels, seg_starts, seg_ends = read_segs(filename)
    stream= segs_to_stream(labels,seg_starts,seg_ends)
    pylab.plot(stream)
    pylab.show()
