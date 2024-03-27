import pandas as pd
import wfdb
import numpy as np
import argparse

def convert_to_wfdb(input_file, output_path, gain):
    # Load the EKG data
    ekg_data = pd.read_csv(input_file, header=None)
    ekg_values = ekg_data.values[:,1]
    ekg_values = ekg_values - np.mean(ekg_values)

    # Normalize signal if necessary, here assuming the signal is already appropriately scaled
    signals = np.array([ekg_values]).T

    # Derive record name from the input file name without the '.csv' extension
    record_name = input_file.split('/')[-1].replace('.csv', '')

    # Write the WFDB record
    wfdb.wrsamp(record_name=record_name,
                fs=250,  # Sampling frequency
                units=['mV'],  # Units
                sig_name=['ECG'],  # Signal names
                p_signal=signals,
                adc_gain=[gain],  # Configurable gain
                baseline=[0],  # Configurable baseline
                fmt=['16'],  # Format
                write_dir=output_path)

def main():
    parser = argparse.ArgumentParser(description="Convert CSV EKG data to WFDB format.")
    parser.add_argument("input_file", help="Path to the input CSV file containing EKG data.")
    parser.add_argument("output_path", help="Path to the directory where the WFDB files will be saved.")
    parser.add_argument("--gain", type=float, default=200, help="Gain used for the signal. Default is 200.")
    
    args = parser.parse_args()
    
    convert_to_wfdb(args.input_file, args.output_path, args.gain)
    
    print(f"Conversion complete. Files saved to {args.output_path}")

if __name__ == "__main__":
    main()
