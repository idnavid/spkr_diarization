import os
import tools
import sys
import pylab
import numpy as np
from sklearn.decomposition import PCA


def run_sad(attr,fs=16000.):
    wavname = attr['audio']
    sadname = attr['sad']
    path = tools.set_path()
    command = '%s/ssad -m 1.0 -a -s -f %s %s %s'
    exe_cmd = command%(path['audioseg'],str(fs),wavname,sadname)
    os.system(exe_cmd)
    return


#-----------------------------------
# Combo-SAD
def autocorr(x):
    rxx = np.correlate(x, x, mode='full')
    return rxx[rxx.size/2:]


def harmonicity(s_framed):
    """calculate harmonicity per frame;
    maximum value of relative autocorrelation
    """
    row,col = s_framed.shape
    rss = np.array([autocorr(fr) for fr in s_framed])
    harm_num = np.array([max(rss[fr_idx,2*8:16*8]) for fr_idx in range(row)])
    harm_den = np.array([(rss[fr_idx,0] - harm_num[fr_idx]) for fr_idx in range(row)])
    return np.divide(harm_num,harm_den)

def clarity(s_framed):
    row,col = s_framed.shape
    rss = np.array([autocorr(fr) for fr in s_framed]) # compute autocorrelation per frame
    enrgs = np.kron(np.ones((col,1)), rss[:,0])
    beta = 1 # find an optimum lag-dependent beta for this. beta should be beta(k)
    amdf_approx = beta*np.sqrt(2*(enrgs.T-rss))
    return np.array([max(amdf_approx[fr_idx,2*8:16*8])/min(amdf_approx[fr_idx,2*8:16*8]) for fr_idx in range(row)])

def periodicity(s_framed):
    "Use harmonic product spectrum (frequency domain)"
    row,col = s_framed.shape
    rss = np.array([autocorr(fr) for fr in s_framed]) # compute autocorrelation per frame
    n_fft = 1024
    rss_freq = np.log(
                      abs(
                       np.array(
                        [
                         np.fft.fft(rss[fr_idx,:],n_fft)[:n_fft/2] for fr_idx in range(row)
                        ]
                       )
                      )+1e-7
                     )
    warped_freqs = np.zeros(rss_freq.shape)
    for i in range(1,8):
        down_sampled = rss_freq[:,0:n_fft/2:2]
        zero_pad_size = (row,n_fft/2 - len(down_sampled[0,:]))
        warped_freqs  = warped_freqs +  np.concatenate((down_sampled, np.zeros(zero_pad_size)), axis=1)
    p_hps = np.array([max(warped_freqs[fr_idx,60*n_fft/8000:500*n_fft/8000]) for fr_idx in range(row)])
    return p_hps

def hard_threshold(sad_feat_1):
    """
    Hard threshold 1-dimensional feature.
    """
    return (sad_feat_1>1.5)*1.

def run_combosad(attr):
    """
    comboSAD uses a combination of acoustic features 
    to calculate 'robust' unsupervised SAD labels.
    """
    fs,s = tools.read_wav(attr['audio'])
    #s = s[:500000]
    # 25 msec, 10 msec, 16KHz
    frame_size = int(0.025*fs)
    frame_shift = int(0.010*fs)
    s_framed = tools.enframe(s,frame_size,frame_shift)
    
    sad_feat = np.zeros((3,s_framed.shape[0]))

    # Feature 1
    sad_feat[0,:] = harmonicity(s_framed)
    
    # Feature 2
    sad_feat[1,:] = clarity(s_framed)
    
    # Feature 3
    sad_feat[2,:] = periodicity(s_framed)
    
    
    # normalize
    sad_feat = sad_feat - np.mean(sad_feat,axis=1)[:,np.newaxis]
    sad_feat = np.divide(sad_feat,np.std(sad_feat,axis=1)[:,np.newaxis]+1e-7)
    n_components = 1
    sad_feat_compressed = PCA(n_components).fit_transform(sad_feat.T)
    return hard_threshold(sad_feat_compressed)



if __name__=='__main__':
    wavname = '/Users/navidshokouhi/Downloads/unimaquarie/projects/ami_sample/amicorpus/ES2002a/audio/ES2002a.Mix-Headset.wav'
    basename = tools.gen_uid(wavname)
    sadname = './%s_sad.txt'%(basename)
    attr = {'sad':sadname,
            'audio':wavname}
    x = run_combosad(attr)
    fs,s = tools.read_wav(attr['audio'])
    pylab.plot(s)
    pylab.plot(tools.deframe(x,25*16,10*16))
    pylab.show()
