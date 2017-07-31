import os
import tools


def run_mfcc(attr,fs=16000.):
    wavname = attr['audio']
    featname = attr['mfcc']
    path = tools.set_path()
    command = '%s/sfbcep -Z -D -A -m -f %s %s %s'
    exe_cmd = command%(path['spro'],str(fs),wavname,featname)
    os.system(exe_cmd)
    return


if __name__=='__main__':
    wavname = '/Users/navidshokouhi/Downloads/unimaquarie/projects/ami_sample/amicorpus/ES2002a/audio/ES2002a.Mix-Headset.wav'
    basename = tools.gen_uid(wavname)
    featname = './%s.mfcc'%basename
    attr = {'mfcc':featname,
            'audio':wavname}
    run_mfcc(attr)
