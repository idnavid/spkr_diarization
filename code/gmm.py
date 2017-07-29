import tools
import sad
import feat
import sys
import os

def train(filelist,out='./out_dir/',model='UBM'):
    fin = open(filelist)
    ubm_list = out+'ubm.lst'
    fout = open(ubm_list,'w')
    for i in fin:
        wavname = i.strip()
        basename = tools.gen_uid(wavname)
        # SAD
        sadname = '%s/%s_sad.txt'%(out,basename)
        sad.run_sad(wavname,sadname)
        
        # MFCC
        featname = '%s/%s_feat.mfc'%(out,basename)
        feat.run_mfcc(wavname,featname)

        fout.write(featname+' '+sadname+'\n')
    fin.close()
    fout.close()
    
    path = tools.set_path()
    ubmname = '%s/%s'%(out,model)
    command = '%s/sgminit -q --label=speech --file-list=%s %s'
    exe_cmd = command%(path['audioseg'],ubm_list,ubmname)
    os.system(exe_cmd)
    return ubmname


def adapt(featname,clustname,cluster,ubmname,out='./out_dir/'):
    mfcc_and_segs = featname+' '+clustname
    scriptname = out+'adapt.script'
    fout = open(scriptname,'w')
    fout.write(mfcc_and_segs)
    fout.close()

    command='%s/sgmestim --map=%s --update=%s --label=%s --output=%s --file-list=%s %s'
    path = tools.set_path()
    gamma = str(0.5) # adaptation coefficient
    params = 'wmv' # adapt these parameters, w:weights, m:means, v:vars
    gmmname = out+cluster
    exe_cmd=command%(path['audioseg'],gamma,params,cluster,gmmname,scriptname,ubmname)
    os.system(exe_cmd)
    return gmmname


if __name__=='__main__':
    ubmlist = sys.argv[1]
    train(ubmlist)
