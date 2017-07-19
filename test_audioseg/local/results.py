# Script to interpret diarization results on a audio file. 
import numpy as np
from scipy.io import wavfile
import pylab


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

def time_to_sample(time_stamp,fs):
    """
       Convert time value in seconds to sample. """
    return 1 + int(time_stamp*fs)

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
    N = segment_ends[-1]
    stream = np.zeros((N,1))
    print labels.shape
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
    return label_stream

if __name__=='__main__':
    fname='/Users/navidshokouhi/Downloads/unimaquarie/projects/ami_sample/amicorpus/ES2002a/audio/ES2002a.Mix-Headset.wav'
    fs,s = read_wav(fname)
    fs = 16000.
    segname='/Users/navidshokouhi/Software_dir/spkr_diarization/test_audioseg/out_dir/ES2002a.clusters'
    labels = read_segs(segname,fs)
    pylab.plot(s)
    pylab.plot(labels/40.)
    pylab.show()
    #print len(labels)



