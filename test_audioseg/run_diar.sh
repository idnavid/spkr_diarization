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

# Generating SAD labels. I've manually tested the SAD for 
# a single file. Seems fine, but will have to do a more 
#rigorous testing later.  
ssad -m 1.0 -a -s -f $fs $wavname ${out}/${fname}.sad

# Extracting MFCC features. 
# NOTE: I haven't figured out how to check the features. 
# I'll have to judge based on the system performance. 
sfbcep -Z -D -A -m -f $fs $wavname ${out}/${fname}.mfcc

# BIC segmentation
sbic --segmentation=${out}/${fname}.sad --label=speech ${out}/${fname}.mfcc ${out}/${fname}.bic

# clustering 
scluster -i -n 2 --label=unk ${out}/${fname}.mfcc ${out}/${fname}.bic ${out}/${fname}.clusters
