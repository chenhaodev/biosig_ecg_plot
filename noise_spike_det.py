#!/usr/bin/env python
# coding: utf-8

import os
import wfdb
import matplotlib.pyplot as plt
import numpy as np

def detect_ekg_spikes(signal, fs=240, median_signal=5, threshold=50, window_size=60):
    """
    Detect spike noise in an ECG/EKG signal using amplitude thresholding.
    """
    window_size = 60 * fs
    
    diff_signal = signal - median_signal
    spike_mask = np.abs(diff_signal) > threshold
    
    return spike_mask

def generate_spike_alerts(spike_mask, fs, alert_window=30*60):
    """
    Generate alerts every 'alert_window' seconds if any spike is detected.
    """
    alert_window_samples = alert_window * fs
    num_windows = len(spike_mask) // alert_window_samples
    
    alerts = []
    for i in range(num_windows):
        start = i * alert_window_samples
        end = start + alert_window_samples
        window_spike_mask = spike_mask[start:end]
        if np.any(window_spike_mask):
            start_time = start / fs
            end_time = end / fs
            alerts.append((start_time, end_time))
    
    return alerts

# Specify the directory containing the ECG/EKG files
#data_dir = '/Users/chenhao/Github/biosig_ecg_plot/gehealth-ekg/50_mit_data_files/'  #path/to/data/directory
data_dir = './' 

# Loop over the files in the directory
for filename in os.listdir(data_dir):
    if filename.endswith('.dat'):  # or any other file extension for your ECG/EKG files
        record_name = os.path.splitext(filename)[0]
        #record_path = os.path.join(data_dir, filename)
        record_path = os.path.join(data_dir, record_name)
        
        # Load the ECG/EKG record
        signals, fields = wfdb.rdsamp(record_path)
        
        # Detect spike noise and generate alerts
        spike_mask = detect_ekg_spikes(signal=signals[:, 0], fs=240, median_signal=5, threshold=50, window_size=60)
        alerts = generate_spike_alerts(spike_mask, fs=240, alert_window=30*60)

        # Write alerts to a log file
        log_filename = f"{record_name}.alert.txt"
        log_file_path = os.path.join(data_dir, log_filename)
        with open(log_file_path, 'w') as log_file:
            for start_time, end_time in alerts:
                log_file.write(f"Alert! Spike noise detected between {start_time:.2f} and {end_time:.2f} seconds.\n")
