#! /usr/bin/bash


# Test script to run diarization on a single file using audioseg. 
# This is a standalone implementation and doesn't use background
# speaker models. 
# Audioseg uses SPro to extract speech features. 
. path.sh
fname=ES2002a
wavname=~/data/ami_sample/amicorpus/ES2002a/audio/${fname}.Mix-Headset.wav 
fs=16000.0
out=out_dir/
trn=train/

SAD(){
inwav=$1
outseg=$2
# Generating SAD labels. I've manually tested the SAD for 
# a single file. Seems fine, but will have to do a more 
#rigorous testing later.  
ssad -m 1.0 -a -s -f $fs $inwav $outseg
}
#SAD $wavname ${out}/${fname}.sad

MFCC(){
inwav=$1
outmfcc=$2
# Extracting MFCC features. 
# NOTE: I haven't figured out how to check the features. 
# I'll have to judge based on the system performance. 
sfbcep -Z -D -A -m -f $fs $inwav $outmfcc
}
#MFCC $wavname ${out}/${fname}.mfcc


BIC(){
# BIC segmentation
sbic --segmentation=${out}/${fname}.sad --label=speech ${out}/${fname}.mfcc ${out}/${fname}.bic
}

CLUSTER(){
# clustering 
scluster -i -n 2 --label=unk ${out}/${fname}.mfcc ${out}/${fname}.bic ${out}/${fname}.clusters
}


TRAIN_UBM(){
# Train a background model using development data

# SAD
nfile=0
while IFS='' read -r wav || [[ -n "$wav" ]]; do 
   SAD $wav ${out}/ubm_${nfile}.sad
   MFCC $wav ${out}/ubm_${nfile}.mfcc
   nfile=$((nfile + 1))
done < ${trn}/ubm.list
ls ${out}/ubm_*.sad > ${trn}/sad.list
ls ${out}/ubm_*.mfcc > ${trn}/mfcc.list
paste -d ' ' ${trn}/mfcc.list ${trn}/sad.list > ${trn}/mfcc_sad.list
sgminit -q --label=speech --file-list=${trn}/mfcc_sad.list ${trn}/ubm.mdl
}
#TRAIN_UBM

TRAIN_GMMS(){
# Find top N clusters. 
python local/tools.py ${out}/${fname}.clusters | sed -e 's/^/C/' > ${out}/${fname}.models
mfcc_file="${out}/${fname}.mfcc"
seg_file="${out}/${fname}.clusters"
echo "$mfcc_file $seg_file" > ${out}/adapt.script
while IFS='' read -r C || [[ -n "$C" ]]; do
   sgmestim --map=0.5 --update=wmv --label=${C} --output=${out}/${C}.mdl --file-list=${out}/adapt.script ${trn}/ubm.mdl
   nfile=$((nfile + 1))
done < ${out}/${fname}.models
}
TRAIN_GMMS

# VITERBI
sviterbi out_dir/hmm_trans.mdl out_dir/ES2002a.mfcc out_dir/hmm.mdl

