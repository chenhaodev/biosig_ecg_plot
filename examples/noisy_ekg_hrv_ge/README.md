This example demonstrates how to extract EKG data from GE Healthcare using the WFDB format, identify spike noise, and create NN-intervals for subsequent HRV analysis and potential arrhythmia findings.

### how to use? 

```python
git clone https://github.com/chenhaodev/sig-ecgplot-db ; cp sig-ecgplot-db/example-db/noisy_ekg_hrv_ge/* . ; cat Case106.part1.dat Case106.part2.dat Case106.part3.dat > Case106.dat # Fetch and copy all .dat and .hea files to the current directory 

python step1_noise_spike_detect.py # generate xxx.alert.txt files indicating where spike noises have been detected.

python step2_nn_intervals_gen.py   # produce xxx.timebgn-timeend.nni.txt files, generating NN intervals for each segment while excluding noise segments.

python step3_nn_hist_analysis.py   # plot an NN interval histogram and employs GMM to assess the number of distributions. Two or more distributions suggest the presence of arrhythmia in the segment. More analysis can be found in xxx.timebgn-timeend.nna.txt
```
