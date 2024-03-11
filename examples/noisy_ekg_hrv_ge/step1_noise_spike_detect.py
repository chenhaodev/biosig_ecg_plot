import os
import wfdb
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def detect_ekg_spikes(signal, fs=240, median_signal=5, threshold=50, window_size=60):
    """
    Detect spike noise in an ECG/EKG signal using amplitude thresholding.
    """
    window_size = 60 * fs
    
    diff_signal = signal - median_signal
    spike_mask = np.abs(diff_signal) > threshold
    
    return spike_mask

def generate_spike_alerts(spike_mask, fs, alert_window=10*60): 
    """
    Generate alerts every 'alert_window' seconds if any spike is detected. (default: every 10 min)
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

def process_ekg_files(data_dir):
    """
    Process ECG/EKG files in the specified directory and generate spike noise alerts.
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
            
            # Detect spike noise and generate alerts every 10 min
            spike_mask = detect_ekg_spikes(signal=signals[:, 0], fs=240, median_signal=5, threshold=50, window_size=60)
            alerts = generate_spike_alerts(spike_mask, fs=240, alert_window=10*60)

            # Write alerts to a log file
            log_filename = f"{record_name}.alert.txt"
            log_file_path = os.path.join(data_dir, log_filename)
            with open(log_file_path, 'w') as log_file:
                for start_time, end_time in alerts:
                    log_file.write(f"Alert! Spike noise detected between {start_time:.2f} and {end_time:.2f} seconds.\n")
            
            logging.info(f"Processed file: {filename}")
        except Exception as e:
            logging.error(f"Error processing file '{filename}': {str(e)}")

# Specify the directory containing the ECG/EKG files
data_dir = './'

# Process ECG/EKG files and generate spike noise alerts
process_ekg_files(data_dir)
