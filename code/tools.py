import os
import sys
import uuid

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
    audioseg_path ='/Users/navidshokouhi/Software_dir/audioseg_dir/audioseg-1.1/src/'
    return {'spro':spro_path,'audioseg':audioseg_path}

def gen_uid(wavname):
    """
    Generate unique id based on input wavname.
    """
    basename = wavname.split('/')[-1]
    basename = basename[:-4] # Do not include .wav extention
    basename = '%s_%s'%(basename,str(uuid.uuid4().fields[-1])[:5])
    return basename
