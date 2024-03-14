# ECG plot

![example 12 lead plot](https://github.com/chenhaodev/biosig_ecg_plot/blob/master/example_ecg.png)

## Plot standard ECG chart from data.
* Support both direct plotting and plotting SVG preview in browser (currently only works on mac)
* Support saving PNG and SVG to disk. e.g. `ecg_plot.plot(ecg, title='12L ekg'); ecg_plot.save_as_svg('example_ecg')`
* Support customer defined lead order
* Support customer defined column count

## Notice
* Input data should be m x n matrix, which m is lead count of ECG and n is length of single lead signal.
* Default sample rate is 500 Hz.

## Example


#### Plot 12 lead ECG


params:

|parameter|description|
| --- | --- |
|ecg        | m x n ECG signal data, which m is number of leads and n is length of signal. |
|sample_rate| Sample rate of the signal. |
|title      | Title which will be shown on top off chart
|lead_index | Lead name array in the same order of ecg, will be shown on left of signal plot, defaults to ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'] |
|lead_order | Lead display order |
|columns    | display columns, defaults to 2 |
|style      | display style, defaults to None, can be 'bw' which means black white |
|row_height |   how many grid should a lead signal have |
|show_lead_name | show lead name |
|show_grid      | show grid |
|show_separate_line  | show separate line |


```python
import ecg_plot

ecg = load_data() # load data should be implemented by yourself 
ecg_plot.plot(ecg, sample_rate = 500, title = 'ECG 12')
ecg_plot.show()
```

#### Plot single lead ECG

```python
import ecg_plot

ecg = load_data() # load data should be implemented by yourself 
ecg_plot.plot_1(ecg[1], sample_rate=500, title = 'ECG')
ecg_plot.show()
```

#### Save result as png

```python
import ecg_plot

ecg = load_data() # load data should be implemented by yourself 
ecg_plot.plot_12(ecg, sample_rate = 500, title = 'ECG 12')
ecg_plot.save_as_png('example_ecg','tmp/')
```

#### Plot 30 second ECG from wfdb format
```bash
git clone https://github.com/chenhaodev/sig-ecgplot-db ; cp sig-ecgplot-db/example-db/noisy_ekg_hrv_ge/* . ; cat Case106.part1.dat Case106.part2.dat Case106.part3.dat > Case106.dat ; 
python ecg_plot1_ekg_30sec_cli.py Case106 0 30
```

#### One step script: de-noise, calculate nni, check potential arrhy, plot segments
```bash
#prepare dataset
cd examples/noisy_ekg_hrv_ge/ ; 
git clone https://github.com/chenhaodev/sig-ecgplot-db ; cp sig-ecgplot-db/example-db/noisy_ekg_hrv_ge/* . ; 
cat Case106.part1.dat Case106.part2.dat Case106.part3.dat > Case106.dat ; rm Case106.part* ; 

#ekg analysis
python step1_noise_spike_detect.py #detect noise    
python step2_nn_intervals_gen.py #generate nn interval while skipping noise period. 
python step3_nn_hist_analysis.py #analysis nn interval using GMM. 
python step4_potential_arrhy.py > Case106.segment.list #identify potential arrhy segment.

#ekg plot (potential arrhy segment)
cp step5_segment_plot.py ../../ ; cp Case106.dat ../../ ; cp Case106.hea ../../ ;  cp Case106.segment.list ../../ ; cd - 
python step5_segment_plot.py Case106.segment.list # it check all (on, off) in xxx.segment.list, and iteratively call function eca_plot1_eka_30sec_cli.py to plot png. 
```
