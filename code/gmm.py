import tools
import sad
import feat
import sys
import os

def train(filelist,out='./out_dir/',model='UBM_0'):
    fin = open(filelist)
    ubm_list = out+model
    fout = open(ubm_list,'w')
    for i in fin:
        wavname = i.strip()
        basename = tools.gen_uid(wavname)
        featname = '%s/%s_feat.mfc'%(out,basename)
        sadname = '%s/%s_sad.txt'%(out,basename)
        attr = {'mfcc':featname,'sad':sadname}
        # SAD
        sad.run_sad(attr)
        
        # MFCC
        feat.run_mfcc(attr)

        fout.write(attr['mfcc']+' '+attr['sad']+'\n')
    fin.close()
    fout.close()
    
    path = tools.set_path()
    ubmname = '%s/%s'%(out,model)
    command = '%s/sgminit -q --label=speech --file-list=%s %s'
    exe_cmd = command%(path['audioseg'],ubm_list,ubmname)
    os.system(exe_cmd)
    return ubmname


def adapt(attr,cluster,ubmname,out='./out_dir/'):
    featname = attr['mfcc']
    clustname = attr['cluster']
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
