import wfdb
import numpy as np
import argparse
import pandas as pd
from scipy.signal import butter, filtfilt, find_peaks

class SignalProcessing:
    def __init__(self, fs=250):
        self.fs = fs

    def bandpass_filter(self, signal, lowcut, highcut, order=5):
        nyquist = 0.5 * self.fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band')
        return filtfilt(b, a, signal)

class EKGProcessor:
    def __init__(self, fs=250, baseline=170, window_size=20):
        self.fs = fs
        self.baseline = baseline
        self.window_size = window_size
        self.signal_processing = SignalProcessing(fs)

    def process_csv_ekg(self, input_file, output_file):
        ekg_data = pd.read_csv(input_file, header=None)
        ekg_values = ekg_data.values[:, 1] - np.mean(ekg_data.values[:, 1]) # + self.baseline
        timestamps = ekg_data.values[:, 0]

        bandpass_filtered_ekg = self.signal_processing.bandpass_filter(ekg_values, 0.5, 50, order=4)

        # Create a DataFrame with the cleaned signal and timestamps
        cleaned_data = pd.DataFrame({'Timestamp': timestamps, 'EKG': bandpass_filtered_ekg})

        # Save the cleaned signal to a new CSV file
        cleaned_data.to_csv(output_file, index=False)

        return bandpass_filtered_ekg, timestamps

    def process_wfdb_ekg(self, record_name, channel_id, start_sec, end_sec):
        signals, fields = wfdb.rdsamp(record_name)
        fs = fields['fs']
        num_samples = signals.shape[0]
        timestamps = np.arange(num_samples) / fs

        idx_start = int(start_sec * fs)
        idx_end = int(end_sec * fs)

        idx_start = max(idx_start, 0)
        idx_end = min(idx_end, num_samples - 1)

        ekg_signal = signals[idx_start:idx_end, channel_id]
        plot_timestamps = timestamps[idx_start:idx_end]

        return ekg_signal, plot_timestamps, fs

def main():
    parser = argparse.ArgumentParser(description='Plot EKG signal for a given record and time range.')
    parser.add_argument('--input', type=str, required=True, help='The input EKG data file (WFDB or CSV format)')
    parser.add_argument('--channel', type=int, default=0, help='The channel of the record to plot (for WFDB format)')
    parser.add_argument('--start', type=int, default=0, help='The start time in seconds for the plot')
    parser.add_argument('--end', type=int, default=30, help='The end time in seconds for the plot')
    parser.add_argument('--output', type=str, help='The output file name for the plotted image')
    parser.add_argument('--fs', type=int, default=250, help='The sampling frequency of the EKG signal')
    parser.add_argument('--baseline', type=int, default=170, help='The baseline value to add to the EKG signal (for CSV format)')
    parser.add_argument('--window_size', type=int, default=20, help='The window size for moving average filtering')

    args = parser.parse_args()

    processor = EKGProcessor(fs=args.fs, baseline=args.baseline, window_size=args.window_size)

    if args.input.endswith('.dat'):
        ekg_signal, plot_timestamps, fs = processor.process_wfdb_ekg(args.input, args.channel, args.start, args.end)
    elif args.input.endswith('.csv'):
        output_file = args.output or f"{args.input}_cleaned.csv"
        ekg_signal, plot_timestamps = processor.process_csv_ekg(args.input, output_file)
        fs = args.fs
    else:
        raise ValueError('Unsupported input file format. Please provide a WFDB (.dat) or CSV file.')

if __name__ == '__main__':
    main()