import wfdb
import numpy as np
from biosppy.signals import ecg

def load_alerts(alert_file):
    alerts = []
    with open(alert_file, 'r') as f:
        for line in f:
            start, end = line.split('between ')[1].split(' and ')
            start = float(start)
            end = float(end.split(' seconds.')[0])
            alerts.append((start, end))
    return alerts

def concat_non_noisy_segments(signal, fs, alerts):
    non_noisy_segments = []
    start = 0
    prev_baseline_amplitude = None

    for i, (alert_start, alert_end) in enumerate(alerts):
        alert_start_sample = int(alert_start * fs)
        alert_end_sample = int(alert_end * fs)
        non_noisy_segment = signal[start:alert_start_sample]
        curr_baseline_amplitude = np.mean(non_noisy_segment)

        if i > 0:
            # Calculate the average NN interval from the last 20 beats of the previous segment
            prev_segment = non_noisy_segments[-1]
            prev_rpeaks = ecg.ecg(prev_segment, fs, show=False)[2]
            if len(prev_rpeaks) > 20:
                prev_nn_intervals = np.diff(prev_rpeaks[-20:] / fs)
                prev_avg_nn = np.mean(prev_nn_intervals)
            else:
                prev_avg_nn = None

            # Calculate the average NN interval from the first 20 beats of the current segment
            curr_rpeaks = ecg.ecg(non_noisy_segment, fs, show=False)[2]
            if len(curr_rpeaks) > 20:
                curr_nn_intervals = np.diff(curr_rpeaks[:20] / fs)
                curr_avg_nn = np.mean(curr_nn_intervals)
            else:
                curr_avg_nn = None

            if prev_avg_nn is not None and curr_avg_nn is not None:
                # Adjust the non-noisy segment based on the average NN intervals
                prev_duration = len(prev_segment) / fs
                curr_duration = len(non_noisy_segment) / fs
                desired_duration = (prev_duration + curr_duration) / 2
                delta_duration = desired_duration - curr_duration

                num_samples_to_add = int(delta_duration * fs)

                if num_samples_to_add > 0:
                    # Compute the average baseline amplitude for the transition
                    if prev_baseline_amplitude is not None:
                        baseline_amplitude = (curr_baseline_amplitude + prev_baseline_amplitude) / 2
                    else:
                        baseline_amplitude = curr_baseline_amplitude

                    # Add sample points with smooth baseline amplitude
                    baseline_segment = np.full(num_samples_to_add, baseline_amplitude)
                    non_noisy_segment = np.concatenate([non_noisy_segment, baseline_segment])
                elif num_samples_to_add < 0:
                    # Remove sample points
                    non_noisy_segment = non_noisy_segment[:num_samples_to_add]

        non_noisy_segments.append(non_noisy_segment)
        start = alert_end_sample
        prev_baseline_amplitude = curr_baseline_amplitude

    non_noisy_segments.append(signal[start:])
    return np.concatenate(non_noisy_segments)

# Load ECG/EKG signal
record_name = 'Case101'
signals, fields = wfdb.rdsamp(record_name)
signal = signals[:, 0]
fs = fields['fs']

# Load alerts
alert_file = f"{record_name}.alert.txt"
alerts = load_alerts(alert_file)

# Concatenate non-noisy segments
non_noisy_signal = concat_non_noisy_segments(signal, fs, alerts)

# Calculate NN intervals using Pan-Tompkins algorithm from biosppy
rpeaks = ecg.ecg(non_noisy_signal, fs, show=False)[2]
nn_intervals = np.diff(rpeaks / fs)

# Print or save the NN intervals
print(nn_intervals)
