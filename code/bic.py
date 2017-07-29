import os
import tools
import sad
import feat

def run_bic(featname,sadname,bicname):
    path = tools.set_path()
    command = '%s/sbic --segmentation=%s --label=speech %s %s'
    exe_cmd = command%(path['audioseg'],sadname,featname,bicname)
    os.system(exe_cmd)
    return


if __name__=='__main__':
    wavname = '/Users/navidshokouhi/Downloads/unimaquarie/projects/ami_sample/amicorpus/ES2002a/audio/ES2002a.Mix-Headset.wav'
    basename = tools.gen_uid(wavname)
    sadname = './%s_sad.txt'%(basename)
    featname = './%s.mfc'%(basename)
    bicname = './%s_bic.txt'%(basename)

    sad.run_sad(wavname,sadname)
    feat.run_mfcc(wavname,featname)
    run_bic(featname,sadname,bicname)
    
