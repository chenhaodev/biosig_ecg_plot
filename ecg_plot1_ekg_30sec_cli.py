import ecg_plot
import wfdb
import numpy as np
import matplotlib.pyplot as plt
import argparse

def plot_ekg(record_name, channel_id, start_sec, end_sec):
    # Read the EKG data and header information
    signals, fields = wfdb.rdsamp(record_name)

    # Extract the sampling frequency from the header information
    fs = fields['fs']

    # Calculate the timestamps for each sample
    num_samples = signals.shape[0]
    timestamps = np.arange(num_samples) / fs

    # Select the range to plot based on the start and end seconds provided
    idx_start = int(start_sec * fs)
    idx_end = int(end_sec * fs)

    # Ensure the indices are within the bounds of the signal
    idx_start = max(idx_start, 0)
    idx_end = min(idx_end, num_samples - 1)

    # Assuming the EKG signal is the first/2nd channel
    #ekg_signal = signals[idx_start:idx_end, 1]
    ekg_signal = signals[idx_start:idx_end, channel_id]
    plot_timestamps = timestamps[idx_start:idx_end]
    return ekg_signal, plot_timestamps

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Plot EKG signal for a given record and time range.')
    parser.add_argument('record_name', type=str, help='The name of the record to plot')
    parser.add_argument('channel_id', type=int, help='The channel of the record to plot', default=0)
    parser.add_argument('start_sec', type=int, help='The start time in seconds for the plot')
    parser.add_argument('end_sec', type=int, help='The end time in seconds for the plot')

    # Parse arguments
    args = parser.parse_args()

    # Call the plot function with the provided arguments
    ekg_signal, plot_timestamps = plot_ekg(args.record_name, args.channel_id, args.start_sec, args.end_sec)

    # Save plotted pic as jpg
    ecg_plot.plot_single_channel_ekg_30sec(ekg_signal, sample_rate=240)
    ecg_plot.save_as_png(args.record_name+'_'+str(args.start_sec)+'_'+str(args.end_sec))

if __name__ == '__main__':
    main()
