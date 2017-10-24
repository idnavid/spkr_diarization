Speaker Diarization component for Alveo project. 
The role of the diarization tool is to segment long speech files into smaller chunks.
The output labels will be used as a benchmark for human transcribers. 

Navid Shokouhi 
July 2017


## Requirements: 
Spro (for feature extraction)
AudioSeg (Diarization binaries)


## Installation guide:
- Installing Spro 4.0
  '''
  cd spro-directory
  ./configure
  make 
  make install 
  '''
NOTE: when installing on Mac, use Spro 5.0


- Installing AudioSeg:
  '''
  cd audioseg-directory
  ./configure --with-spro=[path-to-spro-directory]
  make
  make install
  '''

## diar.py
main module is diar.py. 
diar.py contains example script. To load in python, use diar.diarization(root_dir,wavname,ubmname,out_dir), 
where:
'''
  root_dir: root directory of experiment. 
  wavname: full path to wave file on disk. 
  ubmname: full path to pretrained UBM on disk. 
  out_dir: output directory, to store intermediate files. 
'''
