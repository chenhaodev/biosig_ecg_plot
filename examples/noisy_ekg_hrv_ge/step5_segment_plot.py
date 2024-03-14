import os
import sys

def chunk_segments(filename, onset, offset, chunk_size=30):
    """Generate onset and offset pairs for each 30-second chunk within a segment."""
    duration = offset - onset
    for start in range(onset, offset, chunk_size):
        yield filename, start, min(start + chunk_size, offset)

def main(segment_list_file):
    # Open and read the segment list file
    with open(segment_list_file, 'r') as file:
        segments = file.readlines()

    # Iterate over each segment
    for segment in segments:
        filename, onset_str, offset_str = segment.strip().split(',')
        onset, offset = int(onset_str), int(offset_str)

        # Break down the segment into 30-second chunks and execute the CLI command for each
        for file, chunk_onset, chunk_offset in chunk_segments(filename, onset, offset):
            cmd = f"python ecg_plot1_ekg_30sec_cli.py {file} {chunk_onset} {chunk_offset}"
            os.system(cmd)  # Execute the CLI command
            print(f"Executed: {cmd}")

if __name__ == "__main__":
    #segment_list_file = "Case106.segment.list"
    segment_list_file = sys.argv[1] #"Case106.segment.list"
    main(segment_list_file)
