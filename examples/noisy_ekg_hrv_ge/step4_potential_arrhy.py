import os
import re

def is_abnormal(filename):

    """Check if the file content meets the abnormal criteria."""
    if not filename.endswith('.nna.txt'):
        return None 

    with open(filename, 'r') as file:
        content = file.read()

        # Find all instances of distributions mentioned and their kurtosis values
        distributions = re.findall(r'The NNI data likely follows (\d+) distributions', content)
        kurtosis_values = re.findall(r'Kurtosis: ([\d.]+)', content)

        # Check the criteria for being abnormal
        if distributions:
            num_distributions = int(distributions[0])
            if num_distributions >= 2:
                return True
            elif num_distributions == 1 and kurtosis_values:
                if float(kurtosis_values[0]) < 3.5:
                    return True
        return False

def list_abnormal_filenames():
    """List filenames that meet the abnormal criteria."""
    abnormal_filenames = []

    # Iterate through all files in the current directory
    for filename in os.listdir('.'):
        if os.path.isfile(filename):
            if is_abnormal(filename):
                abnormal_filenames.append(filename)

    return abnormal_filenames

def parse_filename(filename):
    """
    Parses the filename in the format 'CaseXXX.YYYY.ZZ-YYYY.ZZ.nna.txt'
    and returns a dictionary with the record, onset, and offset extracted.

    Args:
    - filename (str): The filename to parse.

    Returns:
    - dict: A dictionary containing the record, onset, and offset.
    """
    # Regular expression to match the pattern in the filename
    pattern = r'^(Case\d+)\.(\d+)\.\d{2}-(\d+)\.\d{2}\.nna\.txt$'
    match = re.match(pattern, filename)
    if match:
        record, onset, offset = match.groups()
        return record+","+str(int(onset))+","+str(int(offset))
    else:
        # If the filename does not match the expected pattern
        return None

# Execute the function and print out the abnormal filenames
abnormal_filenames = list_abnormal_filenames()
for filename in abnormal_filenames:
    print(parse_filename(filename))
