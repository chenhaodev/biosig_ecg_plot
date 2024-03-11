import os
import wfdb
import numpy as np
from biosppy.signals import ecg
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_alerts(alert_file):
    alerts = []
    with open(alert_file, 'r') as f:
        for line in f:
            start, end = line.split('between ')[1].split(' and ')
            start = float(start)
            end = float(end.split(' seconds.')[0])
            alerts.append((start, end))
    return alerts

def create_noise_mask(alerts, signal_length, fs):
    noise_mask = np.zeros(signal_length, dtype=bool)
    for start, end in alerts:
        start_sample = int(start * fs)
        end_sample = int(end * fs)
        noise_mask[start_sample:end_sample] = True
    return noise_mask

def extract_non_noisy_segments(signal, noise_mask, segment_length):
    non_noisy_segments = []
    start = 0
    while start < len(signal):
        end = start + segment_length
        if end > len(signal):
            end = len(signal)
        segment_mask = noise_mask[start:end]
        if not np.any(segment_mask):
            non_noisy_segments.append((signal[start:end], start, end))
        start = end
    return non_noisy_segments

def calculate_nn_intervals(non_noisy_segments, fs, record_name):
    for segment, start, end in non_noisy_segments:
        rpeaks = ecg.ecg(segment, fs, show=False)[2]
        nn_intervals = np.diff(rpeaks) / fs
        
        start_time = start / fs
        end_time = end / fs
        
        # Save NN intervals to a text file
        output_file = f"{record_name}.{start_time:.2f}-{end_time:.2f}.nni.txt"
        np.savetxt(output_file, nn_intervals, fmt='%.6f')
        logging.info(f"NN intervals saved to {output_file}")

def process_ekg_files(data_dir, segment_length):
    """
    Process ECG/EKG files in the specified directory, mask noise periods, and calculate NN intervals.
    """
    # Check if the specified directory exists
    if not os.path.exists(data_dir):
        logging.error(f"Directory '{data_dir}' does not exist.")
        return

    # Get a list of ECG/EKG files in the directory
    ekg_files = [file for file in os.listdir(data_dir) if file.endswith('.dat')]

    # Check if any ECG/EKG files are found
    if not ekg_files:
        logging.warning(f"No ECG/EKG files found in directory '{data_dir}'.")
        return

    # Process each ECG/EKG file
    for filename in ekg_files:
        record_name = os.path.splitext(filename)[0]
        record_path = os.path.join(data_dir, record_name)
        
        try:
            # Load the ECG/EKG record
            signals, fields = wfdb.rdsamp(record_path)
            fs = fields['fs']
            
            # Load alerts
            alert_file = f"{record_name}.alert.txt"
            alerts = load_alerts(os.path.join(data_dir, alert_file))
            
            # Create noise mask
            noise_mask = create_noise_mask(alerts, len(signals), fs)
            
            # Extract non-noisy segments
            non_noisy_segments = extract_non_noisy_segments(signals[:, 0], noise_mask, segment_length)
            
            # Calculate NN intervals for each non-noisy segment
            calculate_nn_intervals(non_noisy_segments, fs, record_name)
            
            logging.info(f"Processed file: {filename}")
        except FileNotFoundError:
            logging.warning(f"Alert file not found for record: {record_name}")
        except Exception as e:
            logging.error(f"Error processing file '{filename}': {str(e)}")

# Specify the directory containing the ECG/EKG files
data_dir = './'

# Specify the desired segment length (in samples)
segment_length = 10 * 60 * 250  # 10 minutes at 250 Hz sampling rate

# Process ECG/EKG files, mask noise periods, and calculate NN intervals
process_ekg_files(data_dir, segment_length)