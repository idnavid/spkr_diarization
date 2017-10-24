import os
import tools
import sad
import feat

def unifrom_segmentation(bicname,sadname,length=2.,fs=16000.):
    """
    Break speech segments longer than 'length' 
    into smaller equal size segments.
    """
    labels_sad,seg_starts_sad,seg_ends_sad = tools.read_segs(sadname)
    labels_bic = []
    seg_starts_bic = []
    seg_ends_bic = []
    for i in range(len(labels_sad)):
        #print labels_sad[i],seg_starts_sad[i],seg_ends_sad[i]
        if labels_sad[i]==1:
            # labels ==1 means sad detected speech.
            start = seg_starts_sad[i]
            end = start+length
            while (start < end) and (end < seg_ends_sad[i]):
                labels_bic.append(labels_sad[i])
                seg_starts_bic.append(start)
                seg_ends_bic.append(end)
                start = end
                end = start + length
            end = seg_ends_sad[i]
            labels_bic.append(0)
            seg_starts_bic.append(start)
            seg_ends_bic.append(end)
        elif labels_sad[i]==0:
            start = seg_starts_sad[i]
            end = seg_ends_sad[i]
            labels_bic.append(labels_sad[i])
            seg_starts_bic.append(start)
            seg_ends_bic.append(end)
    labels_bic = tools.list_to_array(labels_bic)
    seg_starts_bic = tools.list_to_array(seg_starts_bic)
    seg_ends_bic = tools.list_to_array(seg_ends_bic)
    tools.write_segs(labels_bic,seg_starts_bic,seg_ends_bic,bicname,fs,'uniform')
    return



def run_bic(attr,mode='audioseg'):
    path = tools.set_path()
    sadname = attr['sad']
    featname = attr['mfcc']
    bicname = attr['bic']
    
    if mode=='audioseg':
        command = '%s/sbic --segmentation=%s --label=speech %s %s'
        exe_cmd = command%(path['audioseg'],sadname,featname,bicname)
        os.system(exe_cmd)
        return
    elif mode=='uniform':
        # For cases where we'd rather break the signal
        # into equal length segments.
        segment_lengths = 2.*16000. # in samples
        unifrom_segmentation(bicname,sadname,segment_lengths)
        return
    else:
        raise('Segmentation mode not available!')


if __name__=='__main__':
    wavname = '/Users/navidshokouhi/Downloads/unimaquarie/projects/dolby-annotations/data/1_222_2_7_001-ch6-speaker16.wav'
    basename = tools.gen_uid(wavname)
    sadname = './%s_sad.txt'%(basename)
    featname = './%s.mfc'%(basename)
    bicname = './%s_bic.txt'%(basename)
    attr = {'audio':wavname,
            'sad':sadname,
            'mfcc':featname,
            'bic':bicname}
    sad.run_sad(attr)
    feat.run_mfcc(attr)
    run_bic(attr,'uniform')
    
