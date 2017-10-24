The diarization toolkit comes with a number of useful modules:
- sad: speech/nonspeech detection
- feat: feature extraction
- bic: audio segmentation. Has two options, BIC and uniform.
- cluster: clusters segments
- resegment: applies viterbi decoding to update cluster labels (smoothening)
- gmm: calculates mixture models cluster classes. This is to generate models that are used in viterbi.


Austalk:
The austalk data has an interview style, in which most of the speech belongs to the interviewee.
Because of this, resegmentatoin usually cancels out the interviewer. It seems better to remove resegmentation altogether.
Re segmentation, it looks like uniformly breaking the signal into smaller chunks works better than BIC segmentation. This is reasonable, since BIC doesn't give same length segments, which makes the features extracted for different segments uncompatible.
So the sequence of functions for Austalk data is:

audio --> SAD --> Uniform Segmenation --> Clustering
