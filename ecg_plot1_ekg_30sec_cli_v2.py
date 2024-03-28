import ecg_plot
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

    def pan_tompkins_qrs_detect(self, signal):
        filtered_signal = self.bandpass_filter(signal, 5, 15)
        diff_signal = np.diff(filtered_signal)
        squared_signal = diff_signal ** 2
        window_size = int(0.12 * self.fs)
        averaged_signal = np.convolve(squared_signal, np.ones(window_size) / window_size, mode='same')
        threshold = np.mean(averaged_signal) * 0.5
        peaks, _ = find_peaks(averaged_signal, height=threshold, distance=int(0.2 * self.fs))
        return peaks

    def moving_average(self, signal, window_size):
        window = np.ones(window_size) / window_size
        return np.convolve(signal, window, mode='same')

    def combine_ekg(self, bandpass_filtered_ekg, moving_averaged_ekg, qrs_peaks, window_before=0.1, window_after=0.1,
                    window_before_ex=0.025, window_after_ex=0.025, bpfilt_qrs_weight=0.99, mafilt_pt_weight=0.8,
                    max_gap_window=20, min_peak_distance=0.01, peak_threshold=0.2, smoothing_window=5):
        combined_ekg = moving_averaged_ekg.copy()
        min_peak_distance = int(min_peak_distance * self.fs)
        peak_threshold = np.mean(bandpass_filtered_ekg) * peak_threshold

        for peak in qrs_peaks:
            orig_start = max(0, int(peak - window_before * self.fs))
            orig_end = min(len(bandpass_filtered_ekg), int(peak + window_after * self.fs))

            window_after_peak = bandpass_filtered_ekg[peak:orig_end]
            min_peaks, _ = find_peaks(-window_after_peak, distance=min_peak_distance, height=-peak_threshold)
            updated_end = min(int(peak + min_peaks[0] + window_after_ex * self.fs), orig_end) if len(min_peaks) > 0 else orig_end

            window_before_peak = bandpass_filtered_ekg[orig_start:peak]
            min_peaks, _ = find_peaks(-window_before_peak, distance=min_peak_distance, height=-peak_threshold)
            updated_start = max(int(orig_start + min_peaks[-1] - window_before_ex * self.fs), orig_start) if len(min_peaks) > 0 else orig_start

            combined_ekg[updated_start:updated_end] = (
                bandpass_filtered_ekg[updated_start:updated_end] * bpfilt_qrs_weight +
                moving_averaged_ekg[updated_start:updated_end] * (1 - bpfilt_qrs_weight)
            )

            for gap_start, gap_end in [(orig_start, updated_start), (updated_end, orig_end)]:
                if gap_start < gap_end:
                    gap_size = gap_end - gap_start
                    window_size = min(gap_size, max_gap_window)
                    weights = np.ones(window_size) / window_size

                    filtered_gap = np.convolve(bandpass_filtered_ekg[gap_start:gap_end], weights, mode='same')
                    smoothed_gap = np.convolve(moving_averaged_ekg[gap_start:gap_end], weights, mode='same')

                    combined_ekg[gap_start:gap_end] = (
                        smoothed_gap * mafilt_pt_weight +
                        filtered_gap * (1 - mafilt_pt_weight)
                    )

        combined_ekg = np.convolve(combined_ekg, np.ones(smoothing_window) / smoothing_window, mode='same')
        return combined_ekg

class EKGProcessor:
    def __init__(self, fs=250):
        self.fs = fs
        self.signal_processing = SignalProcessing(fs)

    def process_csv_ekg(self, input_file):
        ekg_data = pd.read_csv(input_file, header=None)
        ekg_values = ekg_data.values[:, 1] + 170
        timestamps = ekg_data.values[:, 0]

        bandpass_filtered_ekg = self.signal_processing.bandpass_filter(ekg_values, 0.5, 50, order=4)
        moving_averaged_ekg = self.signal_processing.moving_average(bandpass_filtered_ekg, window_size=20)

        qrs_peaks = self.signal_processing.pan_tompkins_qrs_detect(bandpass_filtered_ekg)
        combined_ekg = self.signal_processing.combine_ekg(bandpass_filtered_ekg, moving_averaged_ekg, qrs_peaks)

        return combined_ekg, timestamps

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
    parser.add_argument('--format', type=str, choices=['wfdb', 'csv'], required=True, help='The format of the input data')
    parser.add_argument('--record', type=str, help='The name of the record to plot (for WFDB format)')
    parser.add_argument('--channel', type=int, default=0, help='The channel of the record to plot (for WFDB format)')
    parser.add_argument('--start', type=int, help='The start time in seconds for the plot (for WFDB format)')
    parser.add_argument('--end', type=int, help='The end time in seconds for the plot (for WFDB format)')
    parser.add_argument('--input', type=str, help='The input EKG data file (for CSV format)')
    parser.add_argument('--output', type=str, help='The output file name for the plotted image')

    args = parser.parse_args()

    processor = EKGProcessor()

    if args.format == 'wfdb':
        ekg_signal, plot_timestamps, fs = processor.process_wfdb_ekg(args.record, args.channel, args.start, args.end)
    elif args.format == 'csv':
        ekg_signal, plot_timestamps = processor.process_csv_ekg(args.input)
        fs = 250

    ecg_plot.plot_single_channel_ekg_30sec(ekg_signal, sample_rate=fs)
    output_file = args.output or f"{args.record}_{args.start}_{args.end}.png"
    ecg_plot.save_as_png(output_file)

if __name__ == '__main__':
    main()