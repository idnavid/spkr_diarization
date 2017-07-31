import os
import tools
import sys

def run_sad(attr,fs=16000.):
    wavname = attr['audio']
    sadname = attr['sad']
    path = tools.set_path()
    command = '%s/ssad -m 1.0 -a -s -f %s %s %s'
    exe_cmd = command%(path['audioseg'],str(fs),wavname,sadname)
    os.system(exe_cmd)
    return


if __name__=='__main__':
    wavname = '/Users/navidshokouhi/Downloads/unimaquarie/projects/ami_sample/amicorpus/ES2002a/audio/ES2002a.Mix-Headset.wav'
    basename = tools.gen_uid(wavname)
    sadname = './%s_sad.txt'%(basename)
    attr = {'sad':sadname,
            'audio':wavname}
    run_sad(attr)

